import os
import requests

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from .forms import IntakeForm, AIFeedbackForm, UserExperienceFeedbackForm
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from asgiref.sync import async_to_sync

# Only loads locally if the file exists; does nothing on Render
if os.path.exists(".env"):
    load_dotenv()

async def execute_sales_agent(system_prompt):
    sales_agent = Agent(name="Sales Agent", instructions=system_prompt, model="gpt-5.4")
    # The 'trace' context customizes metadata visible on your OpenAI Dashboard
    with trace("Write a sales email"):
        result = await Runner.run(sales_agent, "Write a sales email")
        return result.final_output