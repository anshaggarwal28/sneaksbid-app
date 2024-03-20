"""
URL configuration for snekasbiddjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from sneaksbid import views
from sneaksbid.views import HomeView, shop, ShoeCreateView,CheckoutView,Payment
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('shop/', views.shop, name='shop'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/<int:item_id>/bid/', views.place_bid, name='place_bid'),
    #path('payment/', views.payment, name='payment'),
    path('process_payment/<str:client_secret>/', views.process_payment, name='process_payment'),
    path('add-shoe/', ShoeCreateView.as_view(), name='add_shoe'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search_sneakers, name='search_sneakers'),

   # path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
   # path('checkout/success/', checkout_success_view, name='checkout_success'),

    # Forgot Password
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_sent.html'), name="password_reset_done"),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_form.html'), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_done.html'), name="password_reset_complete")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
