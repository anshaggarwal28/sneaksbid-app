from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View

from sneaksbid.models import Item


# Create your views here.
class HomeView(ListView):
    template_name = "./sneaksbid/homepage.html"
    queryset = Item.objects.filter(is_active=True)
    context_object_name = 'items'
