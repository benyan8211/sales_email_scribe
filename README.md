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

#### Part 2: Create ```.env``` file and configure AI model

- In the root directory, create a ```.env``` file.
    - Add this in the first line: ```DATABASE_URL=postgres://db_user:db_password@127.0.0.1:5432/db_name```
    - If you want to use **OpenAI** models (requires minimum $5 upfront):
        - Go to ```https://platform.openai.com/```
        - Create an account
        - Put a minimum of ```$5``` in your account's credit balance.
        - Navigate to ```API Keys```
        - Create an API Key
        - In your ```.env``` file, add this in a new line: ```OPENAI_API_KEY=<your_key_here>```
    - If you want to use **Ollama** models (free):
        - Download and install Ollama from ```https://ollama.com/```.
        - Open up a new terminal window and run this command: ```ollama run phi4``` 
        - In your ```.env``` file, add this in a new line: ```OPENAI_BASE_URL=http://localhost:11434/v1```
        - In your ```.env``` file, add this in a new line: ```OPENAI_API_KEY=ollama```
        - In root directory, look for ```scribe_prompt``` folder and open ```utils.py``` file.
        - On ```line 22```, change ```model="gpt-5.4"``` to ```model="phi4"```.

#### Part 3: Boot up Sales Email Scribe

- Open a new terminal window with the root directory of this project as the current working directory.
    - Run this command in the terminal window: ```uv run python3 manage.py runserver```
