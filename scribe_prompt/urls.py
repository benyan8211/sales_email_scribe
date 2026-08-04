from django.urls import path

from . import views

urlpatterns = [
    path('', views.starting_page, name='starting-page'),
    path('intake-form', views.intake_form, name='intake-form'),
    path('submit-form-view', views.submit_form_view, name='submit-form-view'),
    path('review-and-feedback', views.review_and_feedback, name='review-and-feedback'),
    path('slow-processing', views.slow_processing_view, name='slow-processing'),
    path('slow-processing-with-feedback', views.slow_processing_view_with_feedback, name='slow-processing-with-feedback'),
    path('give-ai-feedback-view', views.give_ai_feedback_view, name='give-ai-feedback-view'),
    path('send-ai-generated-email-to-user', views.send_ai_generated_email_to_user, name='send-ai-generated-email-to-user'),
    path('confirmation', views.confirmation, name='confirmation')
]
