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
        "description": "categorise & extract key info from an email, such as task, catagory, contact details, emotion, priority and posible solution, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Short description of the email reply in English"
                },                        
                "priority": {
                    "type": "string",
                    "description": "Try to give a priority score to this email based on importance, from 0 to 10; 10 most important (in English)"
                },
                "task_category": {
                    "type": "string",
                    "description": "Try to categorise this email into categories like those  (in English): 1. software support; 2. invoice-related; 3. receipts; 4. reimbursement; 5. financial report-related; 6. feedback ; 7. customer support; 8. other."
                },
                "emotion":{
                    "type": "string",
                    "description": "Try to perform sentiment analysis on this email based on the tone and emotion then categorise into the following categories in English: 1. extremly satisfied; 2. satisfied; 3. neutral; 4. unsatisfied; 5. extremly unsatisfied"
                },

                "next_step":{
                    "type": "string",
                    "description": "What is the suggested next step to move this forward? (in English)"
                },

                "suggested_reply":{
                    "type": "string",
                    "description": "What is the suggested email reply to this email, use the language same as the email content."
                }
            },
            "required": ["task", "task_category", "priority", "emotion", "next_step", "suggested_reply"]
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
        functions=function_descriptions,
        function_call="auto"
    )

    arguments = response.choices[0]["message"]["function_call"]["arguments"]
    task = eval(arguments).get("task")
    priority = eval(arguments).get("priority")
    task_category = eval(arguments).get("task_category")
    emotion = eval(arguments).get("emotion")
    next_step = eval(arguments).get("next_step")
    suggested_reply = eval(arguments).get("suggested_reply")

    return {
        "task": task,
        "priority": priority,
        "task_category": task_category,
        "emotion": emotion,
        "next_step": next_step,
        "suggested_reply": suggested_reply,
    }