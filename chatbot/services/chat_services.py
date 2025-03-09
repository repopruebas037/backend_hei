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

    order = {
        "waiter_id" : "Any",
        "delivery_id" : "",
        "table_id" : "Any",
        "status" : "Pendiente",
        "order_items":{},
        "total_price":0
    }

    order_items = {}

    developer_prompt = developer_prompt_data.get("prompt", "")
    menu_json = json.dumps(developer_prompt_data.get(
        "menu", []), ensure_ascii=False, indent=2)
    nombre = developer_prompt_data.get("nombre", "")
    developer_prompt = developer_prompt.format(menu=menu_json, nombre=nombre)

    messages = [
        {"role": "developer", "content": json.dumps(developer_prompt)},
        # {"role": "assistant", "content": json.dumps(assistant_prompt)},
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
            # {"role": "assistant", "content": json.dumps(cls.assistant_prompt)},
        ]
    @classmethod
    def get_chat_response(cls, user_prompt):
        """
        Procesa la entrada del usuario y genera una respuesta del chatbot.        

        Parámetros:
        - user_prompt (str): El mensaje ingresado por el usuario.

        Retorna:
        - JsonResponse: Un JSON con la respuesta del chatbot. Si el usuario finaliza el pedido, devuelve un mensaje de confirmación.
        """

        cls.messages.append({"role": "user", "content": user_prompt})

        user_prompt_lower = user_prompt.lower()

        
        #Valida si el usuario termina la interacción con el chat, 
        #si existen productos en la orden
        #la genera, de otro modo el chatbot se despide.         
        if "finalizar" in user_prompt_lower:
            if cls.order:
                cls.generate_order()
                return JsonResponse({"message": "¡Gracias por tu pedido! Estará listo en breve. ¡Que lo disfrutes!"}, status=200)
            return JsonResponse({"message": "¡Con mucho gusto, ten buen día!"}, status=200)
        
        #**************************************************************
        #************** SE EMPIEZA A GENERAR LA ORDEN *****************
        #**************************************************************

        #Se valida si en el mensaje del usuario existe un producto del 
        # menu del restaurante, si es asi guarda el producto en la orden.        
        for item in cls.productos:
            producto_nombre = item.get("nombre", "").lower()
            producto_precio = item.get("precio", 0)

            if producto_nombre in user_prompt_lower:
                if producto_nombre in cls.order_items:
                    cls.order_items[producto_nombre]["cantidad"] += 1
                else:                    
                    cls.order_items[producto_nombre] = {
                        "cantidad": 1,
                        "precio": producto_precio
                    }

        #Se valida si en el mensaje el usuario 
        #pide su plato para llevar o para la mesa                

        pedido_para = "para llevar"
        if pedido_para in user_prompt_lower:
            cls.order["delivery_id"] = "Any"
            cls.order["waiter_id"] = ""

        
        #Realiza la peticion a la api de openAI enviando como 
        #mensajes el historial de mensajes entre el usuario y el chat. 
    
        completion = cls.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=cls.messages,
            temperature=0.7,
            response_format=cls.ChatResponse
        )

        assistant_message = completion.choices[0].message.content

        #Cada respuesta del chatbot se agrega al historial para permitirle 
        #al chatbot almancenar el contexto de la conversación.
        
        cls.messages.append(
            {"role": "assistant", "content": assistant_message})

        return JsonResponse({"message": assistant_message}, status=200)

    @classmethod
    def generate_order(cls):  

        #Calcular el total de la order
        total = sum(item["cantidad"] * item["precio"] for item in cls.order_items.values())
        
        try:
            new_order = {
                "restaurant_id": cls.developer_prompt_data.get("nombre", ""),
                "waiter_id": cls.order.get("waiter_id"),
                "delivery_id": cls.order.get("delivery_id"),
                "table_id": cls.order.get("table_id"),
                "status": cls.order.get("status"),
                "items": cls.order_items,
                "total_price": total,
                "createdAt": datetime.now()
            }
    
            result = cls.order_collection.insert_one(new_order)
            
            cls.order = {}
            cls.order_items = {}
            return JsonResponse({"message": "Order created", "id": str(result.inserted_id)}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    @classmethod
    def save_prompt(cls, prompt):
        _id = prompt.get("_id")
        result = cls.prompts_collection.replace_one(
            {"_id": _id}, prompt, upsert=True)

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
