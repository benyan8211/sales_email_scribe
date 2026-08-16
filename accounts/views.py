import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import LoginForm, SignUpForm
from .tokens import account_activation_token


def signup_view(request):
    """Responsible for processing Sign Up form submission and
    for rendering Sign Up form."""
    if request.method == 'POST':
        try:
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False  # Deactivate account until email verification
                user.save()

                current_site = get_current_site(request)
                subject = '[Sales Email Scribe] Activate Your Account'

                message = render_to_string('accounts/activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                    'protocol': 'http' if settings.DEBUG else 'https',
                })

                if settings.DEBUG:
                    activation_url = f"http://{current_site.domain}/accounts/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_activation_token.make_token(user)}/"
                    print("\n--- LOCALHOST: ACCOUNT ACTIVATION LINK ---")
                    print(activation_url)
                    print("-----------------------------------------\n")
                else:
                    send_mail(
                        subject,
                        message="Please use an HTML-compatible email client.",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email],
                        html_message=message,
                    )
                return render(request, 'accounts/activation_sent.html')
        except requests.exceptions.HTTPError:
            messages.error(request, ("HTTP Request Failed! "
                "Please try again later."))
        except requests.exceptions.ConnectionError:
            messages.error(request, ("Failed to establish a connection "
                "to the server! Please check your internet connection "
                "and try again."))
        except requests.exceptions.Timeout:
            messages.error(request, ("The server is taking too long to respond. "
                "Please try again later."))
        except requests.exceptions.RequestException:
            messages.error(request, ("An unexpected error occurred! "
                "Please try again later."))
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def activate_view(request, uidb64, token):
    """Handles user account activation."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'accounts/activation_success.html')
    else:
        return render(request, 'accounts/activation_invalid.html')

def login_view(request):
    """Handles processing of Login form submission
    and for rendering Login form."""
    if request.method == 'POST':
        try:
            form = LoginForm(request, data=request.POST)
            form = LoginForm(request, data=request.POST)
            form.fields['username'].label = "Email"
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect("/")
        except requests.exceptions.HTTPError:
            messages.error(request, ("HTTP Request Failed! "
                "Please try again later."))
        except requests.exceptions.ConnectionError:
            messages.error(request, ("Failed to establish a connection "
                "to the server! Please check your internet connection "
                "and try again."))
        except requests.exceptions.Timeout:
            messages.error(request, ("The server is taking too long to respond. "
                "Please try again later."))
        except requests.exceptions.RequestException:
            messages.error(request, ("An unexpected error occurred! "
                "Please try again later."))
    else:
        form = LoginForm()
        form.fields['username'].label = "Email"

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Handles user logout."""
    logout(request)
    return redirect('login')
