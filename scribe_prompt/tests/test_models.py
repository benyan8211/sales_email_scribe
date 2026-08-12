from django.test import TestCase
from ..models import Feedback 


class FeedbackModelTest(TestCase):
    def setUp(self):
        self.feedback = Feedback.objects.create(
            username="test@example.com", rating=5, comments="Great service!"
        )

    def test_feedback_creation(self):
        """Test create feedback object is success."""
        self.assertEqual(self.feedback.username, "test@example.com")
        self.assertEqual(self.feedback.rating, 5)
        self.assertEqual(self.feedback.comments, "Great service!")

    def test_string_representation(self):
        """Test the __str__ method."""
        expected_string = "Rating 5 by test@example.com"
        self.assertEqual(str(self.feedback), expected_string)
