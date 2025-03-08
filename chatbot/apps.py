from django.apps import AppConfig
from chatbot.services.prompt_services import PromptService

class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    prompts_cache = {}

    def ready(self):
        PromptService.get_prompts()