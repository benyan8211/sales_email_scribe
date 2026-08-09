from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from accounts.forms import SignUpForm

class SignUpFormTest(TestCase):
    def test_form_valid_data(self):
        """Test that the form is valid when provided with correct data."""
        data = {
            'email': 'testuser@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123'
        }
        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid())

    def test_empty_email_field_fails_validation(self):
        """Test email field is empty returns a validation error."""
        data = {
            'email': '',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = SignUpForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], "This field is required.")

    def test_empty_password1_field_fails_validation(self):
        """Test password1 field is empty returns a validation error."""
        data = {
            'email': 'testuser@example.com',
            'password1': '',
            'password2': 'securepassword123'
        }
        form = SignUpForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "This field is required.")

    def test_empty_password2_field_fails_validation(self):
        """Test password2 field is empty returns a validation error."""
        data = {
            'email': 'testuser@example.com',
            'password1': 'securepassword123',
            'password2': ''
        }
        form = SignUpForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'][0], "This field is required.")

    def test_empty_password1_password2_mismatch_fails_validation(self):
        """Test password1 and password2 are not equal and there is an error."""
        data = {
            'email': 'testuser@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword1234'
        }
        form = SignUpForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'][0], "The two password fields didn’t match.")

    def test_password_help_text_removed(self):
        """Verify that password2 help_text is removed during initialization."""
        form = SignUpForm()
        self.assertIsNone(form.fields['password2'].help_text)

    def test_clean_email_duplicate_throws_error(self):
        """Ensure clean_email raises a ValidationError if the email already exists."""
        # Create an existing user with the target email
        User.objects.create_user(
            username='existing_user@example.com', 
            email='existing_user@example.com', 
            password='password123'
        )
        
        data = {
            'email': 'existing_user@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        form = SignUpForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], "A user with this email already exists.")

    def test_save_sets_username_as_email(self):
        """Verify the custom save method maps the email string onto the username field."""
        data = {
            'email': 'unique_email@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        
        self.assertEqual(user.username, 'unique_email@example.com')
        self.assertEqual(user.email, 'unique_email@example.com')
        self.assertTrue(User.objects.filter(email='unique_email@example.com').exists())
