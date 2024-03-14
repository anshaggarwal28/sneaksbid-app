from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    post_time = models.DateTimeField(default=timezone.now)
    auction_duration = models.DurationField(default=timezone.timedelta(minutes=5))
    image = models.ImageField()
    available = models.BooleanField(default=True)

    @property
    def is_auction_active(self):
        now = timezone.now()
        auction_start_time = self.post_time
        auction_end_time = auction_start_time + timedelta(minutes=5)
        return auction_start_time <= now <= auction_end_time

    def __str__(self):
        return self.title


class Bid(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.bid_amount}"


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.current_bid


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered_items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    order_delivered = models.BooleanField(default=False)
    order_received = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total_ordered_price(self):
        total_price = 0
        for ordered_item in self.ordered_items.all():
            total_price += ordered_item.price
        return total_price
