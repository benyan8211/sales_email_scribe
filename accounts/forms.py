from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2'] # This removes the username input field from the UI

    def clean_email(self):
        email = self.cleaned_data.get("email")
        
        # Check if any user already has this email address in the database
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email address already exists.")
            
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Sets the hidden username field to match the email string
        user.username = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user