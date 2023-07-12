from typing import Any
from django.db import models

# Create your models here.


class Category(models.Model):
    cat_name = models.CharField(max_length=50, blank=True, null=True)
    cat_image = models.ImageField(upload_to="uploads/category/")

    def __str__(self):
        return self.cat_name


class Registration(models.Model):
    first_name = models.CharField(max_length=50, default="", null=True)
    last_name = models.CharField(max_length=50, default="", null=True)
    email = models.EmailField(max_length=50, default="", null=True)
    password = models.CharField(max_length=255, default="", null=True)
    mobile = models.BigIntegerField()
    gender = models.CharField(max_length=50, default="", null=True)

    def __str__(self):
        return self.first_name


class Product(models.Model):
    pro_name = models.CharField(max_length=150, blank=True, null=True)
    pro_image = models.ImageField(upload_to="uploads/product/")
    pro_desc = models.CharField(max_length=150, blank=True, null=True)
    pro_price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.pro_name


class Order(models.Model):
    address = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.BigIntegerField()
    quantity = models.IntegerField()
    price = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Registration, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):                   # dunder method or magic method
        return self.product.pro_name
