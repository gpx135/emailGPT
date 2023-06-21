import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

function_descriptions = [
    {
        "name": "extract_info_from_email",
        "description": "categorise & extract key info from an email, such as task, task catagory, contact details, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Short description of the task"
                },                        
                "priority": {
                    "type": "string",
                    "description": "Try to give a priority score to this email based on importance, from 0 to 10; 10 most important"
                },
                "task_category": {
                    "type": "string",
                    "description": "Try to categorise this email into categories like those: 1. software support; 2. invoice-related; 3. receipts$reimbursment; 4. financial report-related"
                },

                "next_step":{
                    "type": "string",
                    "description": "What is the suggested next step to move this forward?"
                }
            },
            "required": ["task", "task_category", "priority", "next_step"]
        }
    }
]

class Email(BaseModel):
    from_email: str
    content: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
def analyse_email(email: Email):
    content = email.content
    query = f"Please extract key information from this email: {content} "

    messages = [{"role": "user", "content": query}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions = function_descriptions,
        function_call="auto"
    )

    arguments = response.choices[0]["message"]["function_call"]["arguments"]
    task = eval(arguments).get("task")
    priority = eval(arguments).get("priority")
    task_category = eval(arguments).get("task_category")
    next_step = eval(arguments).get("next_step")

    return {
        "task": task,
        "priority": priority,
        "task_category": task_category,
        "next_step": next_step
    }