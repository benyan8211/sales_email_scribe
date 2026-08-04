from django import forms

class IntakeForm(forms.Form):
    company_name = forms.CharField(label="What is your company's name?", max_length=100, help_text="Maximum 100 characters.", 
        error_messages={"required": "Your company's name cannot be blank."})

    product_name = forms.CharField(label="What is the name of the product/service you are trying to sell?", max_length=100, 
        help_text="Maximum 100 characters.", 
        error_messages={"required": "Your company's product/service name cannot be blank."})
    
    product_details = forms.CharField(label="""Please tell us more about what your product does or about the service that you provide. 
        Please be specific.""", widget=forms.Textarea, max_length=2000, 
        help_text="Maximum 2000 characters.", 
        error_messages={"required": "Your company's product/service description cannot be blank."})

    TONE_CHOICES = [
        ('serious', 'Serious'),
        ('fun', 'Fun'),
        ('a_mix_of_both', 'A mix of both'),
        ('i_am_not_sure', 'I am not sure')
    ]
    
    tone_of_email = forms.ChoiceField(
        choices=TONE_CHOICES,
        widget=forms.RadioSelect,
        label="What should be the tone of the sales email?",
        error_messages={"required": "You must select an option."}
    )

    required_css_class = 'required' 

class AIFeedbackForm(forms.Form):
    feedback_box = forms.CharField(label="Please give the AI feedback on how it can improve the email. Please be specific.", 
        widget=forms.Textarea, max_length=2000, 
        help_text="Maximum 2000 characters.", 
        error_messages={"required": "AI feedback cannot be blank."})
    
    required_css_class = 'required' 

class UserExperienceFeedbackForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'star-rating'}),
        label="How was your experience today?"
    )

    user_experience_feedback_box = forms.CharField(label="We'd love to hear your thoughts! Tell us how we did!", 
        required=False,
        widget=forms.Textarea, max_length=2000, 
        help_text="Maximum 2000 characters.", 
        error_messages={"required": "AI feedback cannot be blank."})

    required_css_class = 'required' 