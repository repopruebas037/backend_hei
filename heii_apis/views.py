import json
from datetime import datetime
import pymongo
from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

"""
**********************************
**** ATTENTION!! ****
This is for testing, DELETE AFTER TESTS !!!
**********************************
"""

# Conexión a MongoDB
HEII_MONGO_URI = "mongodb+srv://pruebasrepo037:YCXMhu9R74b2rkov@heibackend.dcjmk.mongodb.net/?retryWrites=true&w=majority&appName=heibackend"
HEII_MONGO_DB_NAME = "heibackend"
HEII_MONGO_DB_NAME2 = "oldjack"

heii_mongo_client = pymongo.MongoClient(HEII_MONGO_URI)
heii_mongo_db = heii_mongo_client[HEII_MONGO_DB_NAME]
heii_mongo_db2 = heii_mongo_client[HEII_MONGO_DB_NAME2]

# Colecciones
restaurant_collection = heii_mongo_db["restaurant"]
order_collection = heii_mongo_db["order"]
audit_collection = heii_mongo_db["auditoria_historicos"]
products_collection = heii_mongo_db2["products"]

# ----------------- REGISTRAR RESTAURANTE -----------------
@csrf_exempt
@require_POST
def register_restaurant(request):
    """
    Registra un nuevo restaurante en la base de datos.
    """
    try:
        data = json.loads(request.body)

        new_restaurant = {
            "nit": data["nit"],
            "name": data["name"],
            "location": data["location"],
            "password": data["password"],
            "createdAt": data.get("createdAt", datetime.utcnow().isoformat()),
            "phone": data["phone"],
            "email": data["email"]
        }

        result = restaurant_collection.insert_one(new_restaurant)
        return JsonResponse({"message": "Restaurant created", "id": str(result.inserted_id)}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ----------------- CREAR PRODUCTO -----------------
@csrf_exempt
@require_POST
def create_product(request):
    """
    Crea un nuevo producto y lo guarda en la auditoría.
    """
    try:
        data = json.loads(request.body)
        nombre = data.get("nombre")
        precio = data.get("precio")
        cantidad = data.get("cantidad")

        if not nombre or precio is None or cantidad is None:
            return JsonResponse({"error": "nombre, precio y cantidad son obligatorios"}, status=400)

        new_product = {
            "nombre": nombre,
            "precio": precio,
            "cantidad": cantidad,
            "createdAt": datetime.utcnow().isoformat()
        }

        # Guardar el producto en la base de datos
        result = products_collection.insert_one(new_product)
        product_id = str(result.inserted_id)

        # Guardar en auditoría
        audit_record = {
            "product_id": product_id,
            "action": "CREATE",
            "data": new_product,
            "timestamp": datetime.utcnow().isoformat()
        }
        audit_collection.insert_one(audit_record)

        return JsonResponse({"message": "Product created", "id": product_id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ----------------- LOGIN RESTAURANTE -----------------
@csrf_exempt
@require_GET
def login_restaurant(request):
    """
    Busca un restaurante por email y devuelve su información.
    """
    try:
        restaurant_email = request.GET.get("email")

        restaurant = restaurant_collection.find_one({"email": restaurant_email})

        if restaurant:
            restaurant["_id"] = str(restaurant["_id"])
            return JsonResponse(restaurant)

        return JsonResponse({"error": f"Restaurant {restaurant_email} not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ----------------- CREAR ORDEN -----------------
@csrf_exempt
@require_POST
def create_order(request):
    """
    Crea una nueva orden y la guarda en la auditoría.
    """
    try:
        data = json.loads(request.body)
        waiter_id = data.get("waiter_id")
        delivery_id = data.get("delivery_id")
        table_id = data.get("table_id")
        status = data.get("status", "Pendiente")
        restaurant_id = data.get("restaurant_id")
        items = data.get("items", [])
        total_price = data.get("total_price", 0)
        created_at = data.get("createdAt", datetime.utcnow().isoformat())

        if not restaurant_id:
            return JsonResponse({"error": "restaurant_id is required"}, status=400)

        new_order = {
            "restaurant_id": restaurant_id,
            "waiter_id": waiter_id,
            "delivery_id": delivery_id,
            "table_id": table_id,
            "status": status,
            "items": items,
            "total_price": total_price,
            "createdAt": created_at
        }

        # Guardar la orden
        result = order_collection.insert_one(new_order)
        order_id = str(result.inserted_id)

        # Guardar en auditoría
        audit_record = {
            "order_id": order_id,
            "action": "CREATE",
            "data": new_order,
            "timestamp": datetime.utcnow().isoformat()
        }
        audit_collection.insert_one(audit_record)

        return JsonResponse({"message": "Order created", "id": order_id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
