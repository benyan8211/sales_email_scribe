from django.contrib.auth.models import User
from django.test import TestCase

from ..forms import AIFeedbackForm, IntakeForm, StarRatingField, StarWidget, UserExperienceFeedbackForm


class IntakeFormTests(TestCase):
    def test_intake_form_with_valid_data(self):
        """Test that the intake form is valid when provided with correct data."""
        valid_data = {
            'company_name': 'Acme Corp',
            'product_name': 'Widget X',
            'product_details': 'A highly efficient widget.',
            "tone_of_email": 'serious'
        }
        form = IntakeForm(data=valid_data)

        self.assertTrue(form.is_valid())
    
    def test_empty_fields_fails_validation(self):
        """Test empty fields returns a validation error."""
        invalid_data = {
            'company_name': '',
            'product_name': '',
            'product_details': '',
            "tone_of_email": ''
        }
        form = IntakeForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('company_name', form.errors)
        self.assertIn('product_name', form.errors)
        self.assertIn('product_details', form.errors)
        self.assertIn('tone_of_email', form.errors)
        self.assertEqual(form.errors['company_name'][0], "Your company's name cannot be blank.")
        self.assertEqual(form.errors['product_name'][0], "Your company's product/service name cannot be blank.")
        self.assertEqual(form.errors['product_details'][0], "Your company's product/service description cannot be blank.")
        self.assertEqual(form.errors['tone_of_email'][0], "You must select an option.")

class AIFeedbackFormTests(TestCase):
    def test_ai_feedback_form_with_valid_data(self):
        """Test that the AI feedback form is valid when provided with correct data."""
        valid_data = {
            'feedback_box': 'Mention that the cost is $100/month'
        }
        form = AIFeedbackForm(data=valid_data)

        self.assertTrue(form.is_valid())
    
    def test_empty_fields_fails_validation(self):
        """Test empty fields returns a validation error."""
        invalid_data = {
            'feedback_box': ''
        }
        form = AIFeedbackForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('feedback_box', form.errors)
        self.assertEqual(form.errors['feedback_box'][0], "AI feedback cannot be blank.")

class StarWidgetTests(TestCase):
    def setUp(self):
        self.widget = StarWidget()
        self.choices = [
            (5, "5"),
            (4, "4"),
            (3, "3"),
            (2, "2"),
            (1, "1"),
        ]
    def test_optgroups(self):
        """Verify that standard flat choices are properly reversed."""
        self.widget.choices = self.choices
        groups = self.widget.optgroups("rating", [])

        self.assertEqual(groups[0][1][0]["value"], 5)
        self.assertEqual(groups[1][1][0]["value"], 4)
        self.assertEqual(groups[2][1][0]["value"], 3)
        self.assertEqual(groups[3][1][0]["value"], 2)
        self.assertEqual(groups[4][1][0]["value"], 1)

class StarRatingFieldTests(TestCase):
    def test_init_sets_widget_and_choices(self):
        """Verify StarWidget used and 5-to-1 choices maintained."""
        field = StarRatingField(choices=[(10, '10')])
        
        expected_choices = [(5, '5'), (4, '4'), (3, '3'), (2, '2'), (1, '1')]
        self.assertEqual(field.choices, expected_choices)
        self.assertIsInstance(field.widget, StarWidget)

class UserExperienceFeedbackFormTests(TestCase):
    def test_user_feedback_form_valid_with_comments(self):
        """Test user feedback form is valid with comments."""
        valid_data = {
            'rating': 5,
            'comments': 'This site rocks!'
        }
        form = UserExperienceFeedbackForm(data=valid_data)

        self.assertTrue(form.is_valid())

    def test_user_feedback_form_valid_without_comments(self):
        """Test user feedback form is valid without comments."""
        valid_data = {
            'rating': 5
        }
        form = UserExperienceFeedbackForm(data=valid_data)

        self.assertTrue(form.is_valid())

    def test_user_feedback_form_without_rating_fails(self):
        """Test user feedback form is invalid without rating."""
        invalid_data = {}
        form = UserExperienceFeedbackForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        self.assertEqual(form.errors['rating'][0], "This field is required.")
