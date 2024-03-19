from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from djstripe.models import StripeModel


# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    post_time = models.DateTimeField(default=timezone.now)
    auction_duration = models.DurationField(default=timezone.timedelta(days=1))  # Auction lasts for 1 day
    image = models.ImageField(upload_to='items/')
    available = models.BooleanField(default=True)

    @property
    def is_auction_active(self):
        now = timezone.now()
        auction_end_time = self.post_time + self.auction_duration
        return self.post_time <= now <= auction_end_time

    @property
    def duration_days(self):
        return self.auction_duration.days

    @property
    def duration_hours(self):
        return self.auction_duration.seconds // 3600

    @property
    def duration_minutes(self):
        return (self.auction_duration.seconds % 3600) // 60
    def __str__(self):
        return self.title


class Bid(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    is_winner = models.BooleanField(default=False)  # Add this field to indicate the winning bid


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


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


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


class Payment(StripeModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100)
    paid = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.description}'


class Shoe(Item):
    # Add shoe-specific fields here if needed, for example:
    size = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.title} - {self.size}"

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    images = models.ImageField(upload_to='user_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
