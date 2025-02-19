from django.http.response import JsonResponse
from django.views.decorators.http import require_POST
import json

import chatbot.services as services

"""
**********************************
**** ATTENTION!! ****
This is for testing, DELETE AFTER TESTS !!!
**********************************
"""
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_POST
def chatbot(request):

    data = json.loads(request.body)
    user_prompt = data["user_prompt"]

    if not user_prompt:
        return JsonResponse({"message": "No prompt provided"}, status=400)

    chat_response = services.get_chat_response(user_prompt)

    return JsonResponse({"message": chat_response}, status=200)
