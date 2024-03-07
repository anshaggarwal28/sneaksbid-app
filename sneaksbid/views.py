from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from sneaksbid.models import Item, Bid
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
from .forms import SignUpForm
from .forms import SignInForm


# Create your views here.
class HomeView(ListView):
    template_name = "./sneaksbid/homepage.html"
    # queryset = Item.objects.filter(is_active=True)
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


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, './sneaksbid/item_detail.html', {'item': item})


def place_bid(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if not item.is_auction_active:
        messages.error(request, "The auction is not currently active.")
        return redirect('item_detail', item_id=item.id)

    if request.method == 'POST':
        bid_amount = Decimal(request.POST.get('bid_amount', 0))
        last_bid = item.bids.last()
        if last_bid and bid_amount <= last_bid.bid_amount:
            messages.error(request, "Your bid must be higher than the current highest bid.")
            return redirect('item_detail', item_id=item.id)
        elif bid_amount <= item.base_price:
            messages.error(request, "Your bid must be higher than the base price.")
            return redirect('item_detail', item_id=item.id)

        Bid.objects.create(item=item, user=request.user, bid_amount=bid_amount)
        messages.success(request, "Bid placed successfully.")
    return redirect('item_detail', item_id=item.id)
