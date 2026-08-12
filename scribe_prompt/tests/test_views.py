import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse, JsonResponse
from django.test import Client, RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from ..views import (
    confirmation,
    give_ai_feedback_view,
    intake_form,
    review_and_feedback,
    send_ai_generated_email_to_user,
    slow_processing_view,
    slow_processing_view_with_feedback,
    submit_feedback_form_view,
    submit_form_view,
)


class TestStartingPageView(SimpleTestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('starting-page')

    def test_starting_page_renders_properly(self):
        """Ensure Starting Page renders propeerly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scribe_prompt/starting_page.html')

class IntakeFormViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='test@example.com',
            password='securepassword123'
        )
        self.url = reverse('intake-form')

    def _add_session_to_request(self, request):
        """Helper to add session support to RequestFactory requests."""
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()

    def test_login_required_redirects_anonymous_user(self):
        """Ensures unauthenticated users are redirected to the login page."""
        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        self._add_session_to_request(request)

        response = intake_form(request)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_sales_email_cleared_from_session(self):
        """Ensures 'sales_email' is deleted from the session if it exists."""
        request = self.factory.get(self.url)
        request.user = self.user
        self._add_session_to_request(request)
        request.session['sales_email'] = ("<html><body><div style='text-align:center;'>"
            "Subject: Unit Test</div><br><p>Content</p></body></html>")
        request.session.save()

        response = intake_form(request)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('sales_email', request.session)

    def test_intake_form_renders_properly(self):
        """Ensures the empty intake form renders properly."""
        request = self.factory.get(self.url)
        request.user = self.user
        self._add_session_to_request(request)

        response = intake_form(request)

        html_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn(('Hello, welcome to Sales Email <span class='
            '"colorful_scribe_text">Scribe</span>!'), html_content)
        self.assertIn(('Please fill out the intake form below '
            'to get started!'), html_content)
        self.assertIn(('<label for="id_company_name" class="required">What is your '
            'company&#x27;s name?</label>'), html_content)
        self.assertIn(('<input type="text" name="company_name" maxlength="100" '
            'required aria-describedby="id_company_name_helptext" '
            'id="id_company_name">'), html_content)
        self.assertIn(('<label for="id_product_name" class="required">What is the '
            'name of the product/service you are trying to '
            'sell?</label>'), html_content)
        self.assertIn(('<input type="text" name="product_name" '
            'maxlength="100" required '
            'aria-describedby="id_product_name_helptext" '
            'id="id_product_name">'), html_content)
        self.assertIn(('<label for="id_product_details" class="required">'
            'Please tell us more '
            'about what your product does or about the service that you provide. '
            'Please be specific.</label>'), html_content)
        self.assertIn(('<textarea name="product_details" cols="40" '
            'rows="10" maxlength="2000" '
            'required aria-describedby="id_product_details_helptext" '
            'id="id_product_details">\n</textarea>'), html_content)
        self.assertIn(('<span class="radio_select_main_label">What should be the '
            'tone of the sales email?</span>'), html_content)
        self.assertIn(('<input type="radio" name="tone_of_email" value="serious" '
            'id="id_tone_of_email_0" required>'), html_content)
        self.assertIn(('<input type="radio" name="tone_of_email" value="fun" '
            'id="id_tone_of_email_1" required>'), html_content)
        self.assertIn(('<input type="radio" name="tone_of_email" value="a_mix_of_both" '
            'id="id_tone_of_email_2" required>'), html_content)
        self.assertIn(('<input type="radio" name="tone_of_email" value="i_am_not_sure" '
            'id="id_tone_of_email_3" required>'), html_content)
        self.assertIn('<button>Next</button>', html_content)

    def test_prepopulates_form_when_returning_with_saved_data(self):
        """Ensures form loads with saved data when edit=true and session data exists."""
        request = self.factory.get(f"{self.url}?edit=true")
        request.user = self.user
        self._add_session_to_request(request)

        mock_form_data = {
            'company_name': 'Test Company LLC',
            'product_name': 'Test Product Pro Max',
            'product_details': 'Test Product Pro Max does everything pro to the max!',
            'tone_of_email': 'fun'
        }
        request.session['saved_form_data'] = mock_form_data
        request.session.save()

        response = intake_form(request)

        html_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn(('<input type="text" name="company_name" '
            'value="Test Company LLC" '
            'maxlength="100" required aria-describedby="id_company_name_helptext" '
            'id="id_company_name">'), html_content)
        self.assertIn(('<input type="text" name="product_name" value="Test Product '
            'Pro Max" maxlength="100" required aria-describedby='
            '"id_product_name_helptext" id="id_product_name">'), html_content)
        self.assertIn(('<textarea name="product_details" cols="40" rows="10" '
            'maxlength="2000" required aria-describedby="id_product_details_helptext" '
            'id="id_product_details">\nTest Product Pro Max does everything pro to '
            'the max!</textarea>'), html_content)
        self.assertIn(('<input type="radio" name="tone_of_email" value="fun" '
            'id="id_tone_of_email_1" required checked>'), html_content)


class SubmitFormViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_successful_form_submission(self):
        """A valid POST saves data to session and returns success message."""
        valid_form_submission_data = {
            'company_name': 'Acme Corp',
            'product_name': 'Widget X',
            'product_details': 'A highly efficient widget.',
            'tone_of_email': 'serious'
        }
        request = self.factory.post(
            '/submit-form-view/',
            data=valid_form_submission_data
        )
        request.session = self.client.session

        response = submit_form_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'Form submitted successfully!')
        self.assertEqual(request.session['company_name'], 'Acme Corp')
        self.assertEqual(request.session['product_name'], 'Widget X')
        self.assertEqual(
            request.session['product_details'],
            'A highly efficient widget.'
        )
        self.assertEqual(request.session['tone_of_email'], 'serious')
        self.assertEqual(
            request.session['saved_form_data']['company_name'],
            'Acme Corp'
        )

    def test_invalid_form_submission(self):
        """An invalid form submission returns error"""
        invalid_data = {}
        request = self.factory.post('/submit-form-view/', data=invalid_data)
        request.session = self.client.session

        response = submit_form_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)

    def test_invalid_request_method_get(self):
        """A GET request is rejected with a 405 status code and error message."""
        request = self.factory.get('/submit-form-view/')

        response = submit_form_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['errors'], 'Invalid request method')

class ReviewAndFeedbackTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='test@example.com',
            password='securepassword123'
        )
        self.url = reverse('review-and-feedback')

    def _add_session_to_request(self, request):
        """Helper to add session support to RequestFactory requests."""
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()

    def test_login_required_redirects_anonymous_user(self):
        """Ensures unauthenticated users are redirected to the login page."""
        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        self._add_session_to_request(request)

        response = intake_form(request)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_review_and_feedback_renders_successfully(self):
        """Ensure that Review and Feedback page renders successfully."""
        request = self.factory.get(self.url)
        request.user = self.user
        self._add_session_to_request(request)

        response = review_and_feedback(request)

        html_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn(('<div class="spinner"></div>'), html_content)

class GiveAIFeedbackViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
    
    def test_successful_ai_feedback_form_submission(self):
        """A valid submission of ai feedback form saves data to session and returns success message."""
        valid_form_submission_data = {
            'feedback_box': 'Mention that cost is $100/month'
        }
        request = self.factory.post(
            '/give-ai-feedback-view/',
            data=valid_form_submission_data
        )
        request.session = self.client.session

        response = give_ai_feedback_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'Form is valid')
        self.assertEqual(request.session['feedback_box'], 'Mention that cost is $100/month')

    def test_invalid_ai_feedback_form_submission(self):
        """An invalid ai feedback form submission returns error"""
        invalid_data = {}
        request = self.factory.post('/give-ai-feedback-view/', data=invalid_data)
        request.session = self.client.session

        response = give_ai_feedback_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
    
    def test_invalid_request_method_ai_feedback_form_get(self):
        """A GET request for ai feedback form is rejected with a 405 status code and error message."""
        request = self.factory.get('/give-ai-feedback-view/')

        response = give_ai_feedback_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['errors'], 'Invalid request method')

class SlowProcessingViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('scribe_prompt.views.execute_sales_agent',
        new_callable=MagicMock)
    @patch('scribe_prompt.views.async_to_sync')
    def test_slow_processing_view_success(self,
        mock_async_to_sync, mock_execute_sales_agent):
        """Test that the ai processing intake form view executes successfully"""
        mock_generated_email = ("<html><body><div style='text-align:center;'>"
            "Subject: Unit Test</div><br><p>Content</p></body></html>")

        mock_async_to_sync.return_value = mock_execute_sales_agent
        mock_execute_sales_agent.return_value = mock_generated_email

        session_data = {
            'company_name': 'Acme Corp',
            'product_name': 'Widget X',
            'product_details': 'A highly efficient widget.',
            'tone_of_email': 'serious'
        }
        request = self.factory.get('/slow-processing/')
        request.session = session_data.copy()

        response = slow_processing_view(request)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertIn(mock_generated_email, response.content.decode())
        self.assertEqual(request.session['sales_email'], mock_generated_email)
        mock_async_to_sync.assert_called_once()
        called_prompt = mock_execute_sales_agent.call_args[0][0]
        self.assertIn("Acme Corp", called_prompt)
        self.assertIn("Widget X", called_prompt)
        self.assertIn("highly efficient", called_prompt)
        self.assertIn("serious", called_prompt)

class SlowProcessingViewWithFeedbackTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('scribe_prompt.views.execute_sales_agent',
        new_callable=MagicMock)
    @patch('scribe_prompt.views.async_to_sync')
    def test_slow_processing_view_success(self,
        mock_async_to_sync, mock_execute_sales_agent):
        """Test that ai processing feedback view executes successfully"""
        mock_generated_email = ("<html><body><div style='text-align:center;'>"
            "Subject: Unit Test</div><br><p>Content with Feedback</p></body></html>")

        mock_async_to_sync.return_value = mock_execute_sales_agent
        mock_execute_sales_agent.return_value = mock_generated_email

        session_data = {
            'company_name': 'Acme Corp',
            'product_name': 'Widget X',
            'product_details': 'A highly efficient widget.',
            'tone_of_email': 'serious',
            'sales_email': ("<html><body><div style='text-align:center;'>"
            "Subject: Unit Test</div><br><p>Content</p></body></html>"),
            'feedback_box': 'Mention that the cost is $100/month'
        }
        request = self.factory.get('/slow-processing-with-feedback/')
        request.session = session_data.copy()

        response = slow_processing_view_with_feedback(request)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertIn(mock_generated_email, response.content.decode())
        self.assertEqual(request.session['sales_email'], mock_generated_email)
        mock_async_to_sync.assert_called_once()
        called_prompt = mock_execute_sales_agent.call_args[0][0]
        self.assertIn("Acme Corp", called_prompt)
        self.assertIn("Widget X", called_prompt)
        self.assertIn("feedback", called_prompt)
        self.assertIn("$100/month", called_prompt)

class SendAIGeneratedEmailToUserView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='test@example.com',
            password='securepassword123'
        )
    
    def _add_session_to_request(self, request):
        """Helper to add session support to RequestFactory requests."""
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()
    
    @patch('scribe_prompt.views.send_mail')
    @patch('scribe_prompt.views.render_to_string')
    @patch('scribe_prompt.views.settings')
    def test_success_send_ai_generated_email_to_user(self, mock_settings, mock_render, mock_send_mail):
        """Test that sending ai generated email to user works."""
        mock_settings.DEBUG = False
        mock_settings.EMAIL_HOST_USER = 'noreply@example.com'
        mock_render.return_value = 'rendered email html content'

        request = self.factory.get('/send-ai-generated-email-to-user/')
        self._add_session_to_request(request)
        request.user = self.user
        request.session['sales_email'] = ("<html><body><div style='text-align:center;'>"
            "Subject: Unit Test</div><br><p>Content</p></body></html>")
        request.session.save()

        response = send_ai_generated_email_to_user(request)

        mock_render.assert_called_once_with(
            'scribe_prompt/ai_generated_email.html',
            {
                'user': self.user,
                'ai_generated_sales_email': request.session['sales_email']
            }
        )
        mock_send_mail.assert_called_once_with(
            '[Sales Email Scribe] Your Requested AI generated sales email',
            message="Please use an HTML-compatible email client.",
            from_email='noreply@example.com',
            recipient_list=[request.user.email],
            html_message='rendered email html content'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'Form submitted successfully!')

class TestConfirmationPageView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('confirmation')
        self.user = User.objects.create_user(
            username='test@example.com',
            password='securepassword123'
        )
    
    def _add_session_to_request(self, request):
        """Helper to add session support to RequestFactory requests."""
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()

    def test_confirmation_page_renders_properly(self):
        """Ensure that confirmation page renders properly."""
        request = self.factory.get(self.url)
        request.user = self.user

        self._add_session_to_request(request)

        response = confirmation(request)
        html_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn(('<h1 class="success_message">Success!</h1>'), html_content)

class SubmitFeedbackFormViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='test@example.com',
            password='securepassword123'
        )
    
    def _add_session_to_request(self, request):
        """Helper to add session support to RequestFactory requests."""
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()
    
    def test_user_feedback_form_submission_success(self):
        """Ensure that user feedback form submission success."""
        valid_form_data = {
            'rating': 4,
            'comments': "This site rocks!"
        }

        request = self.factory.post('/submit-feedback-form-view/', data=valid_form_data)
        self._add_session_to_request(request)
        request.user = self.user
        request.session.save()

        response = submit_feedback_form_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'Form submitted successfully!')

    def test_invalid_user_feedback_form_submission_fails(self):
        """An invalid user feedback form submission returns error"""
        invalid_data = {}
        request = self.factory.post('/submit-feedback-form-view/', data=invalid_data)
        self._add_session_to_request(request)
        request.user = self.user
        request.session.save()

        response = submit_feedback_form_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)

    def test_invalid_request_method_user_feedback_form_get(self):
        """A GET request for user feedback form is rejected with a 405 status code and error message."""
        request = self.factory.get('/submit-feedback-form-view/')

        response = submit_feedback_form_view(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['errors'], 'Invalid request method')

