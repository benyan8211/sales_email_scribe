# Sales Email Scribe

<p align="center">
  <img src="./static/images/sales_email_scribe_logo.png" alt="Website Logo" width="600" height="300">
</p>

This is an AI powered scribe that writes high quality, custom tailored sales emails.

**Live Demo:** https://sales-email-scribe.onrender.com/ 

## Technologies Used 

- Django Framework (Python)
- uv
- OpenAI Agents SDK
- OpenAI GPT-5.4
- Google SMTP
- PostgreSQL
- Render

## Local Setup

After cloning the GitHub repository on your local machine, run this command in terminal: ```uv sync```

Next, run this command: ```uv run python3 manage.py migrate```

### &#10145; Run the project locally:

#### Part 0: IMPORTANT! PLEASE READ!
- Parts of the user experience involve the user receiving emails from our support email account. If you are running this project **locally**, and as part of the experience, you enter in your own email address, you will not actually receive any emails from us! Instead all emails that you would have received from us are printed to standard output. Please look at standard output in
your terminal for the emails as they are integral for having a satisfying user experience. This only applies if you are running our project **locally**. If you are running our project in **production**, you will receive emails from our support email account.

#### Part 1: Modify settings

- In the root directory, find the ```sales_email_scribe``` folder, open it and then open the ```settings.py``` file
    - Change ```DEBUG=False``` to ```DEBUG=True```
    - Change ```ALLOWED_HOSTS = ['sales-email-scribe.onrender.com']``` to ```ALLOWED_HOSTS = ['sales-email-scribe.onrender.com', '127.0.0.1']```
    - Change ```TIME_ZONE``` to the valid IANA time zone name corresponding to the time zone that you are in
    - Save your changes

#### Part 2: Create ```.env``` file and configure AI model

- In the root directory, create a ```.env``` file
    - Add this as the first line of your ```.env``` file: ```DJANGO_SECRET_KEY=key```
    - **Option 1:** Use OpenAI model (requires minimum $5 upfront):
        - Go to ```https://platform.openai.com/```
        - Create an account
        - Put a minimum of ```$5``` in your account's credit balance
        - Navigate to ```API Keys```
        - Create an API Key
        - In your ```.env``` file, add this in a new line: ```OPENAI_API_KEY=<your_key_here>```
        - (Optional) In root directory, look for ```scribe_prompt``` folder and open ```utils.py``` file
        - (Optional) On ```line 22```, you can keep ```model="gpt-5.4"``` as is or change it to a different OpenAI model of your choice
    - **Option 2:** Use Ollama model (free):
        - Download and install Ollama from ```https://ollama.com/```
        - Open up a new terminal window and run this command: ```ollama run phi4``` 
        - In your ```.env``` file, add this in a new line: ```OPENAI_BASE_URL=http://localhost:11434/v1```
        - In your ```.env``` file, add this in a new line: ```OPENAI_API_KEY=ollama```
        - In root directory, look for ```scribe_prompt``` folder and open ```utils.py``` file
        - On ```line 22```, change ```model="gpt-5.4"``` to ```model="phi4"```
        - (Optional) You may change the model to any other Ollama model of your choice
    - Save your changes

#### Part 3: Boot up Sales Email Scribe

- In the root directory, open a new terminal and run this command: ```make run```

### &#10145; Run unit tests:

- In the root directory, open a new terminal and run this command: ```make test```
