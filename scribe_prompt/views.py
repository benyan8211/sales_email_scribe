import os
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse

from .forms import IntakeForm
from dotenv import load_dotenv

# Only loads locally if the file exists; does nothing on Render
if os.path.exists(".env"):
    load_dotenv()

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
            request.session['user_name'] = form.cleaned_data.get('user_name')
            request.session['user_email'] = form.cleaned_data.get('user_email')
            request.session['company_name'] = form.cleaned_data.get('company_name')
            request.session['product_name'] = form.cleaned_data.get('product_name')
            request.session['product_details'] = form.cleaned_data.get('product_details')

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
    company_name = request.session['company_name']
    product_name = request.session['product_name']
    product_details = request.session['product_details']
    system_prompt = f"""You are a sales agent working for {company_name}, a company that is trying to sell {product_name}. 
    
    Here is a description of {product_name}:
    {product_details}

    You are tasked with writing sales emails.
    """
    
    return render(request, 'scribe_prompt/review_and_feedback.html', {'current_step': 2})

def confirmation(request):
    pass
