from django.urls import path

from . import views

urlpatterns = [
    path('', views.starting_page, name='starting-page'),
    path('lead-intake', views.lead_intake, name='lead-intake'),
    path('review-and-feedback', views.review_and_feedback, name='review-and-feedback'),
    path('confirmation', views.confirmation, name='confirmation')
]
