from django.shortcuts import render

# Create your views here.

def starting_page(request):
    return render(request, 'scribe_prompt/starting_page.html')

def lead_intake(request):
    return render(request, 'scribe_prompt/lead_intake.html')

def review_and_feedback(request):
    pass

def confirmation(request):
    pass
