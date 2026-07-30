import os

from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.template.loader import render_to_string

from .forms import IntakeForm
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from asgiref.sync import async_to_sync

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
            request.session['tone_of_email'] = form.cleaned_data.get('tone_of_email')
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
    def stream_response():
        async def execute_sales_agent(system_prompt):
            sales_agent = Agent(name="Sales Agent", instructions=system_prompt, model="gpt-5.4")
            # The 'trace' context customizes metadata visible on your OpenAI Dashboard
            with trace("Write a sales email"):
                result = await Runner.run(sales_agent, "Write a sales email")
                print(result.final_output)
        
        # 1. Yield the top half of the page immediately (with the spinner)
        yield render_to_string('scribe_prompt/review_and_feedback.html', context={'current_step': 2})
        
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
        """

        print(system_prompt)

        async_to_sync(execute_sales_agent)(system_prompt)

        # 3. Yield the final content and a script to hide the spinner
        yield f"""
                <div>
                    <h1>Processing Complete!</h1>
                </div>
            </div> <!-- Closes #content-container -->
            
            <script>
                // Hide the spinner now that the data has arrived
                document.getElementById('loading-container').style.display = 'none';
            </script>
        </body>
        </html>
        """

    # Return a streaming response instead of a standard HttpResponse
    return StreamingHttpResponse(stream_response())

def confirmation(request):
    pass
