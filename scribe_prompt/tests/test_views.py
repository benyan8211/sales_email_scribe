from django.test import SimpleTestCase, Client
from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

from ..views import intake_form
from ..forms import IntakeForm

class TestStartingPageView(SimpleTestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('starting-page') 

    def test_starting_page_renders_properly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scribe_prompt/starting_page.html')

class IntakeFormViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test@example.com', password='securepassword123')
        self.url = reverse('intake-form')  # Adjust URL name as per your urls.py

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
        request.session['sales_email'] = 'test@example.com'
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
        self.assertIn('Hello, welcome to Sales Email <span class="colorful_scribe_text">Scribe</span>!', html_content)
        self.assertIn('Please fill out the intake form below to get started!', html_content)
        self.assertIn('<label for="id_company_name" class="required">What is your company&#x27;s name?</label>', html_content)
        self.assertIn('<input type="text" name="company_name" maxlength="100" required aria-describedby="id_company_name_helptext" id="id_company_name">', html_content)
        self.assertIn('<label for="id_product_name" class="required">What is the name of the product/service you are trying to sell?</label>', html_content)
        self.assertIn('<input type="text" name="product_name" maxlength="100" required aria-describedby="id_product_name_helptext" id="id_product_name">', html_content)
        self.assertIn('<label for="id_product_details" class="required">Please tell us more about what your product does or about the service that you provide. Please be specific.</label>', html_content)
        self.assertIn('<textarea name="product_details" cols="40" rows="10" maxlength="2000" required aria-describedby="id_product_details_helptext" id="id_product_details">\n</textarea>', html_content)
        self.assertIn('<span class="radio_select_main_label">What should be the tone of the sales email?</span>', html_content)
        self.assertIn('<input type="radio" name="tone_of_email" value="serious" id="id_tone_of_email_0" required>', html_content)
        self.assertIn('<input type="radio" name="tone_of_email" value="fun" id="id_tone_of_email_1" required>', html_content)
        self.assertIn('<input type="radio" name="tone_of_email" value="a_mix_of_both" id="id_tone_of_email_2" required>', html_content)
        self.assertIn('<input type="radio" name="tone_of_email" value="i_am_not_sure" id="id_tone_of_email_3" required>', html_content)
