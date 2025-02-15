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
