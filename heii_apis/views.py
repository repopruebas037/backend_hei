from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from bson import ObjectId
import pymongo
import json

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

restaurant_collection = heii_mongo_db['restaurant']
order_collection = heii_mongo_db['order'] #Add order collection

@csrf_exempt
@require_POST
def register_restaurant(request):
    print("registrar resutarante")
    data = json.loads(request.body)
    new_restaurant = {
        "nit": data["nit"],
        "name": data["name"],
        "location": data["location"],
        "password": data["password"],
        "createdAt": data["createdAt"],
        "phone": data["phone"],
        "email": data["email"]
    }

    result = restaurant_collection.insert_one(new_restaurant)
    return JsonResponse({"message": "restaurant created", "id": str(result.inserted_id)}, status=201)

@csrf_exempt
@require_GET
def login_restaurant(request):
    restaurant_email = request.GET.get("email")
    restaurant = restaurant_collection.find_one(
        {"email": restaurant_email}
    )
    if restaurant:
        restaurant["_id"] = str(restaurant["_id"])
        return JsonResponse(restaurant)
    return JsonResponse({"error": f"restaurant {restaurant_email} not found"}, status=404)

@csrf_exempt
@require_POST
def create_order(request):
    """
    Creates a new order.
    """
    try:
        data = json.loads(request.body)
        waiter_id = data.get("waiter_id")
        delivery_id = data.get("delivery_id")
        table_id = data.get("table_id")
        status = data.get("status", "Pendiente") 
        restaurant_id = data.get("restaurant_id")
        items = data.get("items",[]) 
        total_price = data.get('total_price',0)

        if not restaurant_id:
            return JsonResponse({"error": "restaurant_id is required"}, status=400)

        new_order = {
            "restaurant_id": restaurant_id,
            "waiter_id": waiter_id,
            "delivery_id": delivery_id,
            "table_id": table_id,
            "status": status,
            "items":items,
            "total_price":total_price,
            "createdAt": data.get("createdAt")
        }

        result = order_collection.insert_one(new_order)
        return JsonResponse({"message": "Order created", "id": str(result.inserted_id)}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)