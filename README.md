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
2. Change ```DEBUG=False``` to ```DEBUG=True```
3. Change ```ALLOWED_HOSTS = ['sales-email-scribe.onrender.com']``` to ```ALLOWED_HOSTS = ['sales-email-scribe.onrender.com', '127.0.0.1']```
4. Change

```python
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}
```

to: 

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Live Demo

Link: https://sales-email-scribe.onrender.com/ 