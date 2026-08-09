from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages import get_messages
from unittest.mock import patch
import requests

from accounts.views import signup_view

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login') 
        
        # Create a test user in the database
        self.user = User.objects.create_user(
            username="test@example.com", 
            password="securepassword123"
        )

    def test_get_request_renders_login_form(self):
        """Should render the login form properly."""
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
        valid_credentials = {'username': 'test@example.com', 'password': 'securepassword123'}
        response = self.client.post(self.url, data=valid_credentials)
        
        mock_authenticate.assert_called_once_with(
            username='test@example.com', 
            password='securepassword123'
        )
        mock_login.assert_called_once_with(response.wsgi_request, mock_user)
        self.assertRedirects(response, '/')
    
    def test_empty_username_and_password_failure(self):
        """Empty username and password should give error message."""
        invalid_credentials = {'username': '', 'password': ''}
        response = self.client.post(self.url, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['username'][0].message, "This field is required.")

    def test_empty_password_failure(self):
        """A username entered, but a password left empty will result in an error."""
        invalid_credentials = {'username': 'test@example.com', 'password': ''}
        response = self.client.post(self.url, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['password'][0].message, "This field is required.")

    def test_user_does_not_exist_failure(self):
        """username that does not exist will give an error."""
        invalid_credentials = {'username': 'user@example.com', 'password': 'myexamplepasswordmy'}
        response = self.client.post(self.url, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['__all__'][0].message, "Invalid email and/or password.")

    def test_user_exists_but_password_is_incorrect_failure(self):
        """username that does exist, but password is incorrect will result in error."""
        invalid_credentials = {'username': 'test@example.com', 'password': 'securepasswordx'}
        response = self.client.post(self.url, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['__all__'][0].message, "Invalid email and/or password.")
    
    @patch('accounts.views.authenticate')
    def test_http_error_handling(self, mock_authenticate):
        """When HTTPError arises, it should be handled properly."""
        mock_authenticate.side_effect = requests.exceptions.HTTPError()
        valid_credentials = {'username': 'test@example.com', 'password': 'securepassword123'}
        response = self.client.post(self.url, data=valid_credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "HTTP Request Failed! Please try again later.")

    @patch('accounts.views.authenticate')
    def test_connection_error_handling(self, mock_authenticate):
        """When ConnectionError arises, it should be handled properly."""
        mock_authenticate.side_effect = requests.exceptions.ConnectionError()
        valid_credentials = {'username': 'test@example.com', 'password': 'securepassword123'}
        response = self.client.post(self.url, data=valid_credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Failed to establish a connection to the server! Please check your internet connection and try again.")

    @patch('accounts.views.authenticate')
    def test_timeout_error_handling(self, mock_authenticate):
        """When Timeout arises, it should be handled properly."""
        mock_authenticate.side_effect = requests.exceptions.Timeout
        valid_credentials = {'username': 'test@example.com', 'password': 'securepassword123'}
        response = self.client.post(self.url, data=valid_credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The server is taking too long to respond. Please try again later.")

    @patch('accounts.views.authenticate')
    def test_request_error_handling(self, mock_authenticate):
        """When RequestException arises, it should be handled properly."""
        mock_authenticate.side_effect = requests.exceptions.RequestException()
        valid_credentials = {'username': 'test@example.com', 'password': 'securepassword123'}
        response = self.client.post(self.url, data=valid_credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "An unexpected error occurred! Please try again later.")

class SignupViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('signup')
    
    def test_get_request_renders_signup_form(self):
        """Should render the signup form properly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertEqual(response.context['form'].fields['email'].label, "Email")
        self.assertEqual(response.context['form'].fields['password1'].label, "Password")
        self.assertEqual(response.context['form'].fields['password2'].label, "Password confirmation")

    @patch('accounts.views.send_mail')
    @patch('accounts.views.render_to_string')
    @patch('accounts.views.account_activation_token.make_token')
    @patch('accounts.views.urlsafe_base64_encode')
    @patch('accounts.views.settings')
    def test_signup_success_production(self, mock_settings, mock_uid_encode, mock_make_token, mock_render, mock_send_mail):
        """Test successful POST signup under production settings (DEBUG=False)."""
        mock_settings.DEBUG = False
        mock_settings.EMAIL_HOST_USER = 'noreply@example.com'
        mock_uid_encode.return_value = b'mocked_uid'
        mock_make_token.return_value = 'mocked_token'
        mock_render.return_value = 'rendered email html content'

        valid_credentials = {"email": "user@example.com", "password1": "fTApdG5xs3hzhTJVPcnb", "password2": "fTApdG5xs3hzhTJVPcnb"}

        request = self.factory.post(self.url, data=valid_credentials)
        signup_view(request)

        user = User.objects.get(email='user@example.com')
        self.assertFalse(user.is_active)

        mock_render.assert_called_once_with(
            'accounts/activation_email.html',
            {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': b'mocked_uid',
                'token': 'mocked_token',
                'protocol': 'https'
            }
        )

        mock_send_mail.assert_called_once_with(
            '[Sales Email Scribe] Activate Your Account',
            message="Please use an HTML-compatible email client.",
            from_email='noreply@example.com',
            recipient_list=[user.email],
            html_message='rendered email html content'
        )

    @patch('accounts.views.print')
    @patch('accounts.views.settings')
    def test_signup_success_debug_mode(self, mock_settings, mock_print):
        """Test successful POST signup under debug mode prints the activation link."""
        mock_settings.DEBUG = True

        valid_credentials = {"email": "user@example.com", "password1": "fTApdG5xs3hzhTJVPcnb", "password2": "fTApdG5xs3hzhTJVPcnb"}
        
        request = self.factory.post(self.url, data=valid_credentials)
        signup_view(request)

        user = User.objects.get(email='user@example.com')
        self.assertFalse(user.is_active)

        self.assertTrue(mock_print.called)

        first_printed_text = mock_print.call_args_list[0][0][0]

        self.assertEqual(first_printed_text, "\n--- LOCALHOST: ACCOUNT ACTIVATION LINK ---")

    def test_empty_email_password1_and_password2_failure(self):
        """Empty email, password1, and password2 should give error message."""
        invalid_credentials = {'email': '', 'password1': '', 'password2': ''}
        response = self.client.post(self.url, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['email'][0].message, "This field is required.")

    def test_empty_password1_and_password2_failure(self):
        """Empty password1, and password2 should give error message."""
        invalid_credentials = {'email': 'user@example.com', 'password1': '', 'password2': ''}
        response = self.client.post(self.url, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['password1'][0].message, "This field is required.")

    def test_empty_password2_failure(self):
        """Empty password2 should give error message."""
        invalid_credentials = {'email': 'user@example.com', 'password1': 'fTApdG5xs3hzhTJVPcnb', 'password2': ''}
        response = self.client.post(self.url, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['password2'][0].message, "This field is required.")

    def test_password1_and_password2_mismatch_failure(self):
        """Empty password2 should give error message."""
        invalid_credentials = {'email': 'user@example.com', 'password1': 'fTApdG5xs3hzhTJVPcnb', 'password2': 'afTApdG5xs3hzhTJVPcnb'}
        response = self.client.post(self.url, data=invalid_credentials)
        error_dict = response.context['form'].errors.as_data()
        self.assertEqual(error_dict['password2'][0].message, "The two password fields didn’t match.")

    @patch('accounts.views.send_mail')
    def test_http_error_handling(self, mock_send_mail):
        """When HTTPError arises, it should be handled properly."""
        mock_send_mail.side_effect = requests.exceptions.HTTPError()
        valid_credentials = {"email": "user@example.com", "password1": "fTApdG5xs3hzhTJVPcnb", "password2": "fTApdG5xs3hzhTJVPcnb"}
        response = self.client.post(self.url, data=valid_credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "HTTP Request Failed! Please try again later.")

    @patch('accounts.views.send_mail')
    def test_connection_error_handling(self, mock_send_mail):
        """When ConnectionError arises, it should be handled properly."""
        mock_send_mail.side_effect = requests.exceptions.ConnectionError()
        valid_credentials = {"email": "user@example.com", "password1": "fTApdG5xs3hzhTJVPcnb", "password2": "fTApdG5xs3hzhTJVPcnb"}
        response = self.client.post(self.url, data=valid_credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Failed to establish a connection to the server! Please check your internet connection and try again.")

    @patch('accounts.views.send_mail')
    def test_timeout_error_handling(self, mock_send_mail):
        """When Timeout arises, it should be handled properly."""
        mock_send_mail.side_effect = requests.exceptions.Timeout
        valid_credentials = {"email": "user@example.com", "password1": "fTApdG5xs3hzhTJVPcnb", "password2": "fTApdG5xs3hzhTJVPcnb"}
        response = self.client.post(self.url, data=valid_credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The server is taking too long to respond. Please try again later.")

    @patch('accounts.views.send_mail')
    def test_request_error_handling(self, mock_send_mail):
        """When RequestException arises, it should be handled properly."""
        mock_send_mail.side_effect = requests.exceptions.RequestException()
        valid_credentials = {"email": "user@example.com", "password1": "fTApdG5xs3hzhTJVPcnb", "password2": "fTApdG5xs3hzhTJVPcnb"}
        response = self.client.post(self.url, data=valid_credentials)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "An unexpected error occurred! Please try again later.")