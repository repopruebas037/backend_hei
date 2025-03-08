from chatbot.services.prompt_services import PromptService
from openai import OpenAI
from dotenv import load_dotenv
from django.conf import settings
from django.http import JsonResponse
import json
import pymongo
from pydantic import BaseModel
from datetime import datetime


# Cargar variables de entorno
load_dotenv()

HEII_MONGO_URI = "mongodb+srv://pruebasrepo037:YCXMhu9R74b2rkov@heibackend.dcjmk.mongodb.net/?retryWrites=true&w=majority&appName=heibackend"
HEII_MONGO_DB_NAME = "heibackend"


class ChatServices:
    heii_mongo_client = pymongo.MongoClient(HEII_MONGO_URI)
    heii_mongo_db = heii_mongo_client[HEII_MONGO_DB_NAME]

    prompts_collection = heii_mongo_db['prompts']
    order_collection = heii_mongo_db['order']

    UPLOAD_FOLDER = "./static/images/"
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    developer_prompt_data = PromptService.prompts_cache.get("developer", {})
    assistant_prompt = PromptService.prompts_cache.get("assistant", {})
    productos = developer_prompt_data.get("productos", [])
    order = {}
    
    developer_prompt = developer_prompt_data.get("prompt", "")
    menu_json = json.dumps(developer_prompt_data.get("menu", []), ensure_ascii=False, indent=2)
    nombre = developer_prompt_data.get("nombre", "")
    developer_prompt = developer_prompt.format(menu=menu_json, nombre=nombre)
    
    messages = [
            {"role": "developer", "content": json.dumps(developer_prompt)},
            #{"role": "assistant", "content": json.dumps(assistant_prompt)},
        ]
    class ChatResponse(BaseModel):
        message: str
        menu: list[str]

    @classmethod
    def reload_prompts(cls):
        cls.developer_prompt = PromptService.prompts_cache.get("developer", {})
        cls.assistant_prompt = PromptService.prompts_cache.get("assistant", {})
        cls.productos = cls.developer_prompt.get("productos", [])

        cls.messages = [
            {"role": "developer", "content": json.dumps(cls.developer_prompt)},
            #{"role": "assistant", "content": json.dumps(cls.assistant_prompt)},
        ]

    @classmethod
    def get_chat_response(cls, user_prompt):

        cls.messages.append({"role": "user", "content": user_prompt})

        user_prompt_lower = user_prompt.lower()
        
        if "finalizar" in user_prompt_lower:
            cls.generate_order()
            return JsonResponse({"message": "¡Gracias por tu pedido! Estará listo en breve. ¡Que lo disfrutes!"}, status=200)

        # Agregar productos a la orden si están en el menú
        for item in cls.productos: 
            producto_nombre = item.get("nombre", "").lower() 
            palabras_clave = producto_nombre.split() 

            if any(palabra in user_prompt_lower for palabra in palabras_clave):
                cls.order[item.get("nombre")] = cls.order.get(item.get("nombre"), 0) + 1                   
            if item.get("nombre").lower() in user_prompt_lower:
                cls.order[item.get("nombre")] = cls.order.get(item.get("nombre"), 0) + 1

        completion = cls.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=cls.messages,
            temperature=0.7,
            response_format=cls.ChatResponse
        )

        assistant_message = completion.choices[0].message.content
        cls.messages.append({"role": "assistant", "content": assistant_message})

        return JsonResponse({"message": assistant_message}, status=200)

    @classmethod
    def generate_order(cls):                
        try:
            new_order = {
                "restaurant_id": cls.developer_prompt.get("nombre", ""),
                "waiter_id": "",
                "delivery_id": "",
                "table_id": "",
                "status": "Pendiente",
                "items":cls.order,
                "total_price":"",
                "createdAt": datetime.now()
            }

            result = cls.order_collection.insert_one(new_order)
            cls.order = {}
            return JsonResponse({"message": "Order created", "id": str(result.inserted_id)}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
                

    @classmethod
    def save_prompt(cls, prompt):
        _id = prompt.get("_id")
        result = cls.prompts_collection.replace_one({"_id": _id}, prompt, upsert=True)

        if result.upserted_id:
            message = "Prompt created"
            doc_id = str(result.upserted_id)
            status_code = 201
        elif result.modified_count > 0:
            message = "Prompt replaced"
            doc_id = _id
            status_code = 200
        else:
            message = "No changes made"
            doc_id = _id
            status_code = 200

        return JsonResponse({"message": message, "id": doc_id}, status=status_code)
