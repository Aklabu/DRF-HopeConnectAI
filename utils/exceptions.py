from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.utils import timezone

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            "success": False,
            "statusCode": response.status_code,
            "message": response.data.get('detail', 'An error occurred'),
            "timestamp": timezone.now().isoformat(),
            "data": response.data
        }
        response.data = custom_response
    
    return response