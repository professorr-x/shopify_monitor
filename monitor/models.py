from django.db import models

# Create your models here.

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    title = models.CharField(max_length=255)
    handle = models.CharField(max_length=255)
    variant_id = models.CharField(max_length=255)
    variant_title = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add = True)
    available = models.BooleanField()
    image_url = models.CharField(max_length=255)