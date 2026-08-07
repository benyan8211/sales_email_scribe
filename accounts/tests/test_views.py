from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from unittest.mock import patch
import requests

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Ensure 'login' matches the name in your urls.py
        self.url = reverse('login') 
        self.credentials = {'username': 'test@example.com', 'password': 'securepassword123'}
        
        # Create a test user in the database
        self.user = User.objects.create_user(
            username=self.credentials['username'], 
            password=self.credentials['password']
        )

    def test_get_request_renders_login_form(self):
        """GET request should render the form with the modified label."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertEqual(response.context['form'].fields['username'].label, "Email")
        self.assertEqual(response.context['form'].fields['password'].label, "Password")
