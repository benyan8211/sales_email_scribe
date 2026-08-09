from django.db import models


class Feedback(models.Model):
    username = models.CharField(max_length=100)
    rating = models.IntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} by {self.username}"
