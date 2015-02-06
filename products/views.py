from itertools import chain

from django.shortcuts import render_to_response, RequestContext, Http404,HttpResponseRedirect
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.db.models import Q
from .models import Product, Category, ProductImage
from .forms import ProductForm, ProductImageForm
from cart.models import Cart
# Create your views here.

def check_product(user, product):
	if product in request.user.userpurchase.products.all():
		return True
	else:
		return False

def list_all(request):
	products = Product.objects.filter(active=True)
	if request.user.is_authenticated():
		products = Product.objects.filter(active=True).filter(~Q(user = request.user))

	context={
		"products":products,                
	}
	return render_to_response("products/all.html", context, context_instance=RequestContext(request))

def single(request, slug):
	product = Product.objects.get(slug=slug)
	images = ProductImage.objects.filter(product=product)

	#print request.user.userpurchase.products.all()
	categories = product.category_set.all()
	if request.user == product.user:
		edit = True
	else:
		edit = False
	related = []
	if len(categories) >= 1:
		for category in categories:
			products_category = category.product.all()
			for item in products_category:
				if not item == product:
					related.append(item)
	try:
		cart_id = request.session['cart_id']
		cart = Cart.objects.get(id = cart_id)
		for item in cart.cartitem_set.all():
			if item.product == product:
				in_cart = True
	except:
		in_cart = False

	return render_to_response("products/single.html", locals(), context_instance=RequestContext(request))

def edit_product(request, slug):
	instance = Product.objects.get(slug=slug)
	if request.user == instance.user:
		form = ProductForm(request.POST or None, instance = instance)
		if form.is_valid():
			product_edit = form.save(commit=False)
			product_edit.save()
		return render_to_response("products/edit.html", locals(), context_instance=RequestContext(request))
	else:
		raise Http404

def add_product(request):
	if request.user.is_authenticated():
		form = ProductForm(request.POST or None)
		if form.is_valid():
			product_edit = form.save(commit=False)
			product.user = request.user
			product.active = False
			product.slug = slugify(form.cleaned_data['title'])   #automatically creates slug using title
			product_edit.save()
			return HttpResponseRedirect('/products/%s' %(product.slug))
		return render_to_response("products/edit.html", locals(), context_instance=RequestContext(request))
	else:
		raise Http404

def manage_product_image(request, slug):
	try:
		product = Product.objects.get(slug = slug)
	except:
		product = False
	if request.user == product.user:
		queryset = ProductImage.objects.filter(product__slug=slug)
		ProductImageFormset = modelformset_factory(ProductImage, form = ProductImageForm, can_delete = True)
		formset = ProductImageFormset(request.POST or None, request.FILES or None,queryset = queryset)   #depending on foreignkey
		form = ProductImageForm(request.POST or None)
		if formset.is_valid():
			for form in formset:
				instance = form.save(commit = False)
				instance.save();
				#instance.product = product
			if formset.deleted_forms:
				formset.save()
		return render_to_response("products/manage_images.html", locals(), context_instance=RequestContext(request))
	else:
		raise Http404

def search(request):
	try:
		q = request.GET.get('q', '')
	except:
		q = False
	if q:
		query = q
	products_set = Product.objects.filter(										#searching thru products and categories
		Q(title__icontains = q)|
		Q(description__icontains=q)
	)
	category_set = Category.objects.filter(										#searching thru products and categories
		Q(title__icontains = q)|
		Q(description__icontains=q)
	)
	products = list(chain(products_set, category_set))

	'''
	if q:
		query = "seached for %s we got :" %(q)
		k = q.split()
		if len(k) >= 2:
			products = []
			for item in k:
				all_products = Product.objects.filter(title__icontains = item)
				for product in all_products:
					if product not in products:
						products.append(product)
		else:
			products = Product.objects.filter(title__icontains = q)
	'''
	return render_to_response("products/search.html", locals(), context_instance=RequestContext(request))

def user_products(request):
	products = Product.objects.filter(user = request.user)
	return render_to_response("products/all.html", locals(), context_instance=RequestContext(request))



