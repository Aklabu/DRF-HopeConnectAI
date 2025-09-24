from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    verbose_name = 'Chatbot'

    def ready(self):
        # Import signals here to ensure they are registered
        pass