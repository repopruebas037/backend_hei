from django.http import HttpResponse, JsonResponse
from chatbot.services.prompt_services import PromptService
from chatbot.services.chat_services import ChatServices


from django.views.decorators.http import require_POST
import json
import requests
import pymongo


"""
**********************************
**** ATTENTION!! ****
This is for testing, DELETE AFTER TESTS !!!
**********************************
"""
from django.views.decorators.csrf import csrf_exempt

HEII_MONGO_URI = "mongodb+srv://pruebasrepo037:YCXMhu9R74b2rkov@heibackend.dcjmk.mongodb.net/?retryWrites=true&w=majority&appName=heibackend"
HEII_MONGO_DB_NAME = "heibackend"

heii_mongo_client = pymongo.MongoClient(HEII_MONGO_URI)
heii_mongo_db = heii_mongo_client[HEII_MONGO_DB_NAME]

prompts_collection = heii_mongo_db['prompts']

@csrf_exempt
@require_POST
def chatbot(request):

    data = json.loads(request.body)
    user_prompt = data["user_prompt"]

    if not user_prompt:
        return JsonResponse({"message": "No prompt provided"}, status=400)

    return ChatServices.get_chat_response(user_prompt)

@csrf_exempt
@require_POST
def save_prompt(request):

    prompt = json.loads(request.body)    

    if not prompt:
        return JsonResponse({"message": "No prompt provided"}, status=400)

    return ChatServices.save_prompt(prompt)

from django.apps import apps

@csrf_exempt
@require_POST
def reload_prompt(request):
    PromptService.reload_prompts() 
    ChatServices.reload_prompts()
    return JsonResponse({"message":"prompts reloaded"}, status=200)

VERIFICATION_TOKEN = "abcdefg12345"

@csrf_exempt
def verify_whatsapp(request):
    if request.method == "GET":
        print("verifying")
        hub_mode = request.GET.get("hub.mode")
        hub_challenge = request.GET.get("hub.challenge")
        hub_verify_token = request.GET.get("hub.verify_token")

        if hub_mode == "subscribe" and hub_verify_token == VERIFICATION_TOKEN:
            return HttpResponse(hub_challenge) 
        return JsonResponse({"error": "Invalid verification token"}, status=403)
    
    if request.method == "POST":
        data = json.loads(request.body)
        return JsonResponse({"status": "Mensaje recibido"}, status=200)

    return JsonResponse({"error": "Método no permitido"}, status=405)


WHATSAPP_API_KEY = "EAArts55hNvMBOZC8QunzoeW9xQdKCArk9FaquRZBKBxrhxdLBnVTtM1UlVlcnmYG4I0pzu3ZBKKllBQacUBX1YirBf6ZBeo1VZCGv54QiNekenEz6GLYLGiJgApUWs2WB886NOusfMnNOZBIKCCOOrWdPOHOrZAqdmaOVdZCPRCvZCb7oQyUiSMKj9SLzIZCCe2uGD0MfGj7AjbmS2LqZAZBMvU1weFFTfqxZB5jGpdAZD"


@csrf_exempt
def send_whatsapp_message(to):
    url = "https://graph.facebook.com/v22.0/621653484354259/messages"
    headers = {
        "Authorization": f"Bearer " + WHATSAPP_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "body": "Hola"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()
