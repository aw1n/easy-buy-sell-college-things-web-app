from django.db import models
from products.models import Product
from django.contrib.auth.models import User
# Create your models here.

class Orders(models.Model):
	buyer = models.ForeignKey(User, related_name='product_buyer')
	seller = models.ForeignKey(User, related_name='product_seller')
	product = models.ForeignKey(Product)
