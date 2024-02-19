from django.conf import settings
from django.contrib import messages
#from django.sneaksbid.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
# from .forms import CheckoutForm, CouponForm, RefundForm
from .models import Item, Category


# Create your views here.
class HomeView(ListView):
    template_name = "index.html"
    queryset = Item.objects.filter(is_active=True)
    context_object_name = 'items'

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-detail.html"