import os

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from .forms import IntakeForm, AIFeedbackForm, UserExperienceFeedbackForm
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from asgiref.sync import async_to_sync

# Only loads locally if the file exists; does nothing on Render
if os.path.exists(".env"):
    load_dotenv()

# Create your views here.

def starting_page(request):
    return render(request, 'scribe_prompt/starting_page.html')

@login_required(login_url='/accounts/login/')
def intake_form(request):
    if 'sales_email' in request.session:
        del request.session['sales_email']

    is_returning = request.GET.get('edit') == 'true'
    
    if is_returning and 'saved_form_data' in request.session:
        # Prepopulate only if they clicked the back button
        form = IntakeForm(request.session['saved_form_data'])
    else:
        form = IntakeForm()
    
    return render(request, 'scribe_prompt/intake_form.html', {'current_step': 1, 'form': form })

def submit_form_view(request):
    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():            
            request.session['company_name'] = form.cleaned_data.get('company_name')
            request.session['product_name'] = form.cleaned_data.get('product_name')
            request.session['product_details'] = form.cleaned_data.get('product_details')
            request.session['tone_of_email'] = form.cleaned_data.get('tone_of_email')

            request.session['saved_form_data'] = request.POST
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

@login_required(login_url='/accounts/login/')
def review_and_feedback(request):
    form = AIFeedbackForm()
    return render(request, 'scribe_prompt/review_and_feedback.html', { 'current_step': 2, 'form': form })

def give_ai_feedback_view(request):
    if request.method == 'POST':
        form = AIFeedbackForm(request.POST)
        if form.is_valid():            
            request.session['feedback_box'] = form.cleaned_data.get('feedback_box')

            # Return a JSON response instead of a full HTML template
            return JsonResponse({
                'success': True, 
                'message': 'Form is valid'
            })
        else:
            # Return form validation errors to the JavaScript front-end
            return JsonResponse({
                'success': False, 
                'errors': form.errors.get_json_data() 
            }, status=400)
            
    return JsonResponse({'success': False, 'errors': 'Invalid request method'}, status=405)

def slow_processing_view_with_feedback(request):
    async def execute_sales_agent(system_prompt):
            sales_agent = Agent(name="Sales Agent", instructions=system_prompt, model="gpt-5.4")
            # The 'trace' context customizes metadata visible on your OpenAI Dashboard
            with trace("Write a sales email"):
                result = await Runner.run(sales_agent, "Write a sales email")
                return result.final_output
    company_name = request.session['company_name']
    product_name = request.session['product_name']
    sales_email = request.session['sales_email']
    system_prompt = f"""You are a sales agent working for {company_name}, a company that is trying to sell {product_name}. 

    Here is a sales email that you previously wrote:
    {sales_email}

    The user wants you to write a new email. This new email should improve upon that previously written email by taking 
    into account the following feedback:
    {request.session['feedback_box']}

    Be sure to return your response in html. Make the email look aesthetically pleasing. Include the email's subject in a div that is center aligned.
    Add a line break. Then include the html content within the body tag.
    """

    sales_email = async_to_sync(execute_sales_agent)(system_prompt)

    request.session['sales_email'] = sales_email

    return HttpResponse(f"""
        {sales_email}
    """)

def slow_processing_view(request):
    async def execute_sales_agent(system_prompt):
            sales_agent = Agent(name="Sales Agent", instructions=system_prompt, model="gpt-5.4")
            # The 'trace' context customizes metadata visible on your OpenAI Dashboard
            with trace("Write a sales email"):
                result = await Runner.run(sales_agent, "Write a sales email")
                return result.final_output

    if 'sales_email' in request.session:
        return HttpResponse(f"""
            {request.session['sales_email']}
        """)
    company_name = request.session['company_name']
    product_name = request.session['product_name']
    product_details = request.session['product_details']
    tone_of_email = request.session['tone_of_email']
    tone_of_email_description_catalog = {
        "serious": """The tone of the sales email should be serious, and very professional.""",
        "fun": """The tone of the sales email should be fun and lighthearted and contain mild humor.""",
        "a_mix_of_both": """The tone of the sales email should be a mix of serious and fun. 
        It should be professional, but also include hints of mild humor.""",
        "i_am_not_sure": """The tone of the sales email has not been specified. Please use your best judgment."""
    }
    system_prompt = f"""You are a sales agent working for {company_name}, a company that is trying to sell {product_name}. 
    
    Here is a description of {product_name}:
    {product_details}

    You are tasked with writing sales emails.

    {tone_of_email_description_catalog.get(tone_of_email)}

    Be sure to return your response in html. Make the email look aesthetically pleasing. Include the email's subject in a div that is center aligned.
    Add a line break. Then include the html content within the body tag.
    """

    sales_email = async_to_sync(execute_sales_agent)(system_prompt)
    request.session['sales_email'] = sales_email

    return HttpResponse(f"""
        {sales_email}
    """)

@login_required(login_url='/accounts/login/')
def confirmation(request):
    form = UserExperienceFeedbackForm()
    return render(request, 'scribe_prompt/confirmation.html', { 'current_step': 3, 'form': form })

def send_ai_generated_email_to_user(request):
    try: 
        user = request.user
        subject = '[Sales Email Scribe] Your Requested AI generated sales email'
        message = render_to_string('scribe_prompt/ai_generated_email.html', {
            'user': user,
            'ai_generated_sales_email': request.session['sales_email']
        })

        print(message)

        # Send the email message
        send_mail(
            subject, 
            message="Please use an HTML-compatible email client.", 
            from_email=settings.EMAIL_HOST_USER, 
            recipient_list=[user.email],
            html_message=message,
        )

        return JsonResponse({
            'success': True, 
            'message': 'Form submitted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'errors': e
        }, status=400)
