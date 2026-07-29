from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import IntakeForm

# Create your views here.

def starting_page(request):
    return render(request, 'scribe_prompt/starting_page.html')

def intake_form(request):
    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            return HttpResponseRedirect("/review-and-feedback")
        else:
            request.session['form_errors'] = form.errors.get_json_data()
            return HttpResponseRedirect('/intake-form')  # Redirect back to the SAME page (GET request)
    else:
        form = IntakeForm()
        errors = request.session.pop('form_errors', None)
        
    return render(request, 'scribe_prompt/intake_form.html', {'current_step': 1, 'form': form, 'errors': errors })

def review_and_feedback(request):
    return render(request, 'scribe_prompt/review_and_feedback.html', {'current_step': 2})

def confirmation(request):
    pass
