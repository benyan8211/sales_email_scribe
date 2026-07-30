from django.urls import path

from . import views

urlpatterns = [
    path('', views.starting_page, name='starting-page'),
    path('intake-form', views.intake_form, name='intake-form'),
    path('submit-form-view', views.submit_form_view, name='submit-form-view'),
    path('review-and-feedback', views.review_and_feedback, name='review-and-feedback'),
    path('confirmation', views.confirmation, name='confirmation')
]
