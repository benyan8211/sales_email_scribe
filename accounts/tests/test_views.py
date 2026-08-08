from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from unittest.mock import patch
import requests

LOGIN_URL = reverse('login') 

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
        """GET request should render the form properly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertEqual(response.context['form'].fields['username'].label, "Email")
        self.assertEqual(response.context['form'].fields['password'].label, "Password")

    @patch('accounts.views.authenticate')
    @patch('accounts.views.login')
    def test_successful_login(self, mock_login, mock_authenticate):
        """A valid login authentication should redirect to the root URL."""
        # Setup mock user and authentication success
        mock_user = object() 
        mock_authenticate.return_value = mock_user

        response = self.client.post(LOGIN_URL, data=self.credentials)
        
        mock_authenticate.assert_called_once_with(
            username='test@example.com', 
            password='securepassword123'
        )
        mock_login.assert_called_once_with(response.wsgi_request, mock_user)
        self.assertRedirects(response, '/')
    
    def test_empty_username_and_password_failure(self):
        """Empty username and password should give error message."""
        invalid_credentials = {'username': '', 'password': ''}
        response = self.client.post(LOGIN_URL, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['username'][0].message, "This field is required.")

    def test_empty_password_failure(self):
        """A username entered, but a password left empty will result in an error."""
        invalid_credentials = {'username': 'test@example.com', 'password': ''}
        response = self.client.post(LOGIN_URL, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['password'][0].message, "This field is required.")

    def test_user_does_not_exist_failure(self):
        """username that does not exist will give an error."""
        invalid_credentials = {'username': 'user@example.com', 'password': 'myexamplepasswordmy'}
        response = self.client.post(LOGIN_URL, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['__all__'][0].message, "Invalid email and/or password.")

    def test_user_exists_but_password_is_incorrect_failure(self):
        """username that does exist, but password is incorrect will result in error."""
        invalid_credentials = {'username': 'test@example.com', 'password': 'securepasswordx'}
        response = self.client.post(LOGIN_URL, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['__all__'][0].message, "Invalid email and/or password.")
    
    @patch('accounts.views.authenticate')
    def test_http_error_handling(self, mock_authenticate):
        """When HTTPError arises, it should be handled properly."""
        mock_authenticate.side_effect = requests.exceptions.HTTPError()
        response = self.client.post(LOGIN_URL, data=self.credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "HTTP Request Failed! Please try again later.")

    @patch('accounts.views.authenticate')
    def test_connection_error_handling(self, mock_authenticate):
        """When HTTPError arises, it should be handled properly."""
        mock_authenticate.side_effect = requests.exceptions.ConnectionError()
        response = self.client.post(LOGIN_URL, data=self.credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Failed to establish a connection to the server! Please check your internet connection and try again.")

    @patch('accounts.views.authenticate')
    def test_timeout_error_handling(self, mock_authenticate):
        """When HTTPError arises, it should be handled properly."""
        mock_authenticate.side_effect = requests.exceptions.Timeout
        response = self.client.post(LOGIN_URL, data=self.credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The server is taking too long to respond. Please try again later.")

    @patch('accounts.views.authenticate')
    def test_request_error_handling(self, mock_authenticate):
        """When HTTPError arises, it should be handled properly."""
        mock_authenticate.side_effect = requests.exceptions.RequestException()
        response = self.client.post(LOGIN_URL, data=self.credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "An unexpected error occurred! Please try again later.")