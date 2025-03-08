from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from django.conf import settings
import os

from pydantic import BaseModel




load_dotenv()

UPLOAD_FOLDER = "./static/images/"

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Read the restaurant prompt from a txt file
module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, 'prompt.txt')
with open(file_path, "r", encoding="utf-8") as file:
    dev_prompt = file.read()

# Read the assistant prompt from a txt file
file_path = os.path.join(module_dir, 'assistant_prompt.txt')
with open(file_path, "r", encoding="utf-8") as file:
    assistant_prompt = file.read()

# Mensajes iniciales
messages = [    
    {"role": "system", "content": dev_prompt},
    {"role": "assistant", "content": assistant_prompt}
]

menu = {
    "Queen Master": 12,
    "King Master": 15,
    "Jack Master": 3,
    "Magic Master":5
}

order = {}

class ChatResponse(BaseModel):
    message: str
    menu: list[str]

def get_chat_response(user_prompt):

    messages.append({"role": "user", "content": user_prompt})

    user_prompt = user_prompt.lower()

    if "finalizar" in user_prompt:     
        generateOrder()   
        return "¡Gracias por tu pedido! Estará listo en breve. ¡Que lo disfrutes!"

    for item in menu:
        if item.lower() in user_prompt:  
            if item in order:
                order[item] += 1
            else:
                order[item] = 1                

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        store=True,
        messages=messages,
        temperature=0.7,
        response_format=ChatResponse,
    )

    assistant_message = completion.choices[0].message.content

    messages.append({"role": "assistant", "content": assistant_message})

    return assistant_message

def generateOrder():
    print(f"La orden es {order}")
