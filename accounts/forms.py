from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    """Form to enable new users to sign up to website."""
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password2"].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Check if any user already has this email in the database
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Sets the hidden username field to match the email string
        user.username = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    """Form to enable existing users to log in."""
    error_messages = {
        'invalid_login': "Invalid email and/or password.",
    }
