# Sales Email Scribe

This is an AI powered scribe that writes high quality, custom tailored sales emails.

## Technologies Used 

- Django Framework (Python)
- uv
- OpenAI Agents SDK
- Google SMTP
- PostgreSQL
- Render

## Local Setup

After cloning the GitHub repository on your local machine, run this command in terminal: ```uv sync```

**To run the project locally:** 
1. Open ```sales_email_scribe``` folder and find ```settings.py```
    1. Change ```DEBUG=False``` to ```DEBUG=True```
    2. Change ```ALLOWED_HOSTS = ['sales-email-scribe.onrender.com']``` to ```ALLOWED_HOSTS = ['sales-email-scribe.onrender.com', '127.0.0.1']```
2. In the root directory, create a ```.env``` file.
    1. Put this in the file: ```DATABASE_URL=postgres://db_user:db_password@127.0.0.1:5432/db_name```
    2. If you want to use OpenAI Models (requires minimum $5 upfront):
        1. Go to ```https://platform.openai.com/```
        2. Create an account
        3. Put minimum of ```$5``` in your account's credit balance.
        4. Navigate to ```API Keys```
        5. Create an API Key
        6. In ```.env```, add this: ```OPENAI_API_KEY=<your_key_here>```



## Live Demo

Link: https://sales-email-scribe.onrender.com/ 