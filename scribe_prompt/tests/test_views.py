from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from ..views import intake_form


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
