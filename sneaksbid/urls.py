from django.urls import path
from .views import (
    HomeView, ItemDetailView,
)

app_name = 'sneaksbid'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
path('product/<slug>/', ItemDetailView.as_view(), name='product'),

]
