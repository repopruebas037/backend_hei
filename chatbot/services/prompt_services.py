import pymongo

'''
    This class contain the services for the client prompts
'''

HEII_MONGO_URI = "mongodb+srv://pruebasrepo037:YCXMhu9R74b2rkov@heibackend.dcjmk.mongodb.net/?retryWrites=true&w=majority&appName=heibackend"
HEII_MONGO_DB_NAME = "heibackend"

class PromptService:

    '''
        Load the prompts from DB
    '''
    _cache_cargado = False 
    prompts_cache = {}  

    @classmethod
    def get_prompts(cls):

        if not cls._cache_cargado:  # Loads the prompts only if they have not been loaded
            heii_mongo_client = pymongo.MongoClient(HEII_MONGO_URI)
            heii_mongo_db = heii_mongo_client[HEII_MONGO_DB_NAME]
            prompts_collection = heii_mongo_db['prompts']

            prompts = prompts_collection.find({})
            for prompt in prompts:
                cls.prompts_cache[prompt["_id"]] = prompt
            
            cls._cache_cargado = True
            print("**** Loaded prompts:", list(cls.prompts_cache.keys()),"****")

    @classmethod
    def reload_prompts(cls):
        
        heii_mongo_client = pymongo.MongoClient(HEII_MONGO_URI)
        heii_mongo_db = heii_mongo_client[HEII_MONGO_DB_NAME]
        prompts_collection = heii_mongo_db['prompts']

        cls.prompts_cache.clear() 
        prompts = prompts_collection.find({})
        for prompt in prompts:
            cls.prompts_cache[prompt["_id"]] = prompt
        
        cls._cache_cargado = True
        print("Prompts recargados:", list(cls.prompts_cache.keys()))
