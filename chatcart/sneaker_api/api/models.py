from django.db import models

class Product(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    image_url = models.URLField()

class ProductPrice(models.Model):
    product = models.ForeignKey(Product, related_name='prices', on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_level = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
