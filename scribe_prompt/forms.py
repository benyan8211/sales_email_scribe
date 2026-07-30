from django import forms

class IntakeForm(forms.Form):
    user_name = forms.CharField(label='What is your name?', max_length=100, help_text="Maximum 100 characters.", 
        error_messages={"required": "Your name cannot be blank."})

    user_email = forms.EmailField(label="What is your Email Address", max_length=100, help_text="Maximum 100 characters.", 
        error_messages={"required": "Your email address cannot be blank."})

    required_css_class = 'required' 