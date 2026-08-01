from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .forms import SignUpForm
from .tokens import account_activation_token

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email verification
            user.save()
            
            # Gather domain details to construct the verification URL
            current_site = get_current_site(request)
            subject = '[Sales Email Scribe] Activate Your Account'
            
            # Render the email text body from a template
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            print(settings.EMAIL_HOST_USER)
            print([user.email])
            
            # Send the email message
            send_mail(
                subject, 
                message="Please use an HTML-compatible email client.", 
                from_email=settings.EMAIL_HOST_USER, 
                recipient_list=[user.email],
                html_message=message,
            )
            return render(request, 'accounts/activation_sent.html')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def activate_view(request, uidb64, token):
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
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # The user enters an email, but Django processes it in the username field
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
        form.fields['username'].label = "Email Address"

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

