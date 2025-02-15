from django.http.response import JsonResponse
from django.views.decorators.http import require_POST
from dotenv import load_dotenv
from openai import OpenAI
from django.conf import settings
import json
import os

"""
**********************************
**** ATTENTION!! ****
This is for testing, DELETE AFTER TESTS !!!
**********************************
"""
from django.views.decorators.csrf import csrf_exempt

load_dotenv()

UPLOAD_FOLDER = "./static/images/"

client = OpenAI(api_key=settings.OPENAI_API_KEY)


@csrf_exempt
@require_POST
def chatbot(request):
    data = json.loads(request.body)

    user_prompt = data["user_prompt"]
    if not user_prompt:
        return JsonResponse({"message": "No prompt provided"}, status=400)

    # Read the restaurant prompt

    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'prompt.txt')
    with open(file_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    chat_response = completion.choices[0].message.content

    return JsonResponse({"message": chat_response}, status=200)
