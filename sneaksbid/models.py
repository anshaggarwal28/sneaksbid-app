from django.db import models

# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    stock_no = models.CharField(max_length=10)
    description_short = models.CharField(max_length=50)
    description_long = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title