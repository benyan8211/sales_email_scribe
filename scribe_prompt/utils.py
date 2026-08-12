import os

from agents import Agent, Runner, trace
from dotenv import load_dotenv

# Only loads locally if the file exists; does nothing on Render
if os.path.exists(".env"):
    load_dotenv()

async def execute_sales_agent(system_prompt):
    sales_agent = Agent(name="Sales Agent", instructions=system_prompt, model="gpt-5.4")
    with trace("Write a sales email"):
        result = await Runner.run(sales_agent, "Write a sales email")
        return result.final_output
