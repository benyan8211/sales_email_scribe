from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse

from .forms import IntakeForm

# Create your views here.

def starting_page(request):
    return render(request, 'scribe_prompt/starting_page.html')

def intake_form(request):
    form = IntakeForm()
    
    return render(request, 'scribe_prompt/intake_form.html', {'current_step': 1, 'form': form })

def submit_form_view(request):
    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():            
            # Return a JSON response instead of a full HTML template
            return JsonResponse({
                'success': True, 
                'message': 'Form submitted successfully!'
            })
        else:
            # Return form validation errors to the JavaScript front-end
            return JsonResponse({
                'success': False, 
                'errors': form.errors.get_json_data() 
            }, status=400)
            
    return JsonResponse({'success': False, 'errors': 'Invalid request method'}, status=405)


def review_and_feedback(request):
    return render(request, 'scribe_prompt/review_and_feedback.html', {'current_step': 2})

def confirmation(request):
    pass
