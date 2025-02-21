from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from django.conf import settings
import os

from pydantic import BaseModel

load_dotenv()

UPLOAD_FOLDER = "./static/images/"

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class RestaurantMenu(BaseModel):
    message: str
    menu: list[str]


def get_chat_response(user_prompt):

    # Read the restaurant prompt from a txt file
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'prompt.txt')
    with open(file_path, "r", encoding="utf-8") as file:
        dev_prompt = file.read()

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "developer", "content": dev_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=RestaurantMenu,
        temperature=0.2
    )

    return completion.choices[0].message.parsed.model_dump_json()
