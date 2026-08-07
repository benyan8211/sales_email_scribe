# Sales Email Scribe

This is an AI powered scribe that writes high quality, custom tailored sales emails.

**Live Demo:** https://sales-email-scribe.onrender.com/ 

## Technologies Used 

- Django Framework (Python)
- uv
- OpenAI Agents SDK
- Google SMTP
- PostgreSQL
- Render

## Local Setup

After cloning the GitHub repository on your local machine, run this command in terminal: ```uv sync```

### To run the project locally:

#### Part 1: Modify settings

- Open ```sales_email_scribe``` folder and find ```settings.py```
    - Change ```DEBUG=False``` to ```DEBUG=True```
    - Change ```ALLOWED_HOSTS = ['sales-email-scribe.onrender.com']``` to ```ALLOWED_HOSTS = ['sales-email-scribe.onrender.com', '127.0.0.1']```

#### Part 2: Create ```.env``` file and choose AI model

2. In the root directory, create a ```.env``` file.
    1. Add this in the first line: ```DATABASE_URL=postgres://db_user:db_password@127.0.0.1:5432/db_name```
    2. If you want to use **OpenAI** models (requires minimum $5 upfront):
        1. Go to ```https://platform.openai.com/```
        2. Create an account
        3. Put minimum of ```$5``` in your account's credit balance.
        4. Navigate to ```API Keys```
        5. Create an API Key
        6. In ```.env```, add this in a new line: ```OPENAI_API_KEY=<your_key_here>```
    3. If you want to use **Ollama** models (free):
        1. Download and install Ollama from ```https://ollama.com/```.
        2. Open up a new terminal window and run this command: ```ollama run phi4``` 
        3. In ```.env```, add this in a new line: ```OPENAI_BASE_URL=http://localhost:11434/v1```
        4. In ```.env```, add this in a new line: ```OPENAI_API_KEY=ollama```
        5. In root directory, look for ```scribe_prompt``` folder and open ```utils.py``` file.
        6. On ```line 22```, change ```model="gpt-5.4"``` to ```model="phi4"```.
3. Open a new terminal window with the root directory of the project as the current working directory.
    1. Run this command in the terminal window in order to boot up the project: ```uv run python3 manage.py runserver```
