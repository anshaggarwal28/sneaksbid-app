from django.urls import reverse_lazy
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView
from sneaksbid.models import Item, Bid, OrderItem
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from snekasbiddjangoProject import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from .tokens import generate_token
from decimal import Decimal
from django.conf import settings
from .forms import SignUpForm, ShoeForm
from .forms import SignInForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BidForm
from .models import Payment, Shoe
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(ListView):
    template_name = "./sneaksbid/homepage.html"
    context_object_name = 'items'
    ordering = ['-bid_expiry']

    def get_queryset(self):
        return Item.objects.all()

def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            pass1 = form.cleaned_data['pass1']

            user = authenticate(username=username, password=pass1)
            if user is not None:
                login(request, user)
                fname = user.first_name
                # messages.success(request, "Logged In Successfully!!")
                return render(request, "authentication/index.html", {"fname": fname})
            else:
                messages.error(request, "Bad Credentials!!")
                return redirect('home')
    else:
        form = SignInForm()
    return render(request, "authentication/signin.html", {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists! Please try some other username.")
                return redirect('home')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email Already Registered!!")
                return redirect('home')

            if password1 != password2:
                messages.error(request, "Passwords didn't match!!")
                return redirect('home')

            user = form.save(commit=False)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False  # Change to `True` if you don't need email confirmation
            user.save()

            # Send welcome email
            subject = "Welcome to SneaksBid Login!!"
            message = "Hello " + user.first_name + "!! \n" + "Welcome to SneaksBid!! \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address.\n\nThanking You\n"
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            # Send email confirmation
            current_site = get_current_site(request)
            email_subject = "Confirm your Email @ SneaksBid Login!!"
            message2 = render_to_string('email_confirmation.html', {
                'name': user.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            email.fail_silently = True
            email.send()

            messages.success(request,
                             "Your Account has been created successfully! Please check your email to confirm your email address in order to activate your account.")
            return redirect('signin')
        else:
            # Form is not valid
            messages.error(request, "Error processing your form.")
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request, 'activation_failed.html')


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')


def shop(request):
    # Retrieve all items from the database
    sneakers = Item.objects.all()

    context = {
        'sneakers': sneakers,
    }

    return render(request, 'sneaksbid/shop.html', context)


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'sneaksbid/item_detail.html', {'item': item})


@login_required
def place_bid(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if not item.available or not item.is_auction_active:
        messages.error(request, "The auction is not currently active or the item is not available.")
        return redirect('item_detail', item_id=item.id)

    if request.method == 'POST':
        form = BidForm(request.POST, item=item)
        if form.is_valid():
            bid_amount = form.cleaned_data['bid_amount']
            last_bid = item.bids.order_by('-bid_amount').first()
            if last_bid and bid_amount <= last_bid.bid_amount:
                messages.error(request, "Your bid must be higher than the current highest bid.")
                return redirect('place_bid', item_id=item.id)
            elif bid_amount <= item.base_price:
                messages.error(request, "Your bid must be higher than the base price.")
                return redirect('place_bid', item_id=item.id)

            bid = form.save(commit=False)
            bid.item = item
            bid.user = request.user
            bid.save()
            messages.success(request, "Bid placed successfully.")
            return redirect('item_detail', item_id=item.id)
        else:
            messages.error(request, "There was a problem with your bid.")
    else:
        form = BidForm(item=item)

    return render(request, 'sneaksbid/bid.html', {'form': form, 'item': item})

#
# def payment(request):
#     form = PaymentForm(request.POST or None)
#
#     if request.method == "POST":
#         if form.is_valid():
#             payment = form.save(commit=False)
#             payment.user = request.user
#             payment.save()
#
#             # Create a Stripe PaymentIntent
#             stripe.api_key = settings.STRIPE_PRIVATE_KEY
#             intent = stripe.PaymentIntent.create(
#                 amount=int(payment.amount * 100),
#                 currency='usd',
#                 metadata={'payment_id': payment.id}
#             )
#
#             # Redirect to the payment processing view
#             return redirect('process_payment', intent.client_secret)
#
#     context = {'form': form}
#     return render(request, './sneaksbid/payment.html', context)
#
#
# def process_payment(request, client_secret):
#     if request.method == "POST":
#         stripe.api_key = settings.STRIPE_PRIVATE_KEY
#         intent = stripe.PaymentIntent.confirm(client_secret)
#
#         if intent.status == 'succeeded':
#             # Update the Payment model
#             payment_id = intent.metadata['payment_id']
#             payment = Payment.objects.get(id=payment_id)
#             payment.paid = True
#             payment.save()
#
#             messages.success(request, 'Payment successful!')
#             return redirect('success')
#
#     context = {'client_secret': client_secret}
#     return render(request, './sneaksbid/process_payment.html', context)
#
# views.py
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PaymentForm
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def process_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Token is created using Stripe Checkout or Elements!
            token = request.POST.get('stripeToken')  # Use the name attribute from your Stripe form
            try:
                charge = stripe.Charge.create(
                    amount=int(form.cleaned_data['amount'] * 100),  # Amount in cents
                    currency='usd',
                    description='Example charge',
                    source=token,
                )
                Payment.objects.create(
                    user=request.user,
                    amount=form.cleaned_data['amount'],
                    stripe_charge_id=charge.id,
                )
                messages.success(request, 'Payment successful!')
                return redirect('payment_success')
            except stripe.error.StripeError:
                messages.error(request, 'Payment error!')
    else:
        form = PaymentForm()
    return render(request, 'sneaksbid/payment.html', {'form': form, 'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLIC_KEY})



class ShoeCreateView(LoginRequiredMixin, CreateView):
    model = Shoe
    form_class = ShoeForm
    template_name = 'sneaksbid/shoe_form.html'  # Adjust the template path if needed
    success_url = reverse_lazy('home')
    login_url = '/signin/'