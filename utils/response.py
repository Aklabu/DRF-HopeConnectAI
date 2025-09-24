from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status

class CustomResponse:
    @staticmethod
    def success(message, data=None, status_code=200):
        response_data = {
            "success": True,
            "statusCode": status_code,
            "message": message,
            "timestamp": timezone.now().isoformat()
        }
        
        if data is not None:
            response_data["data"] = data
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(message, status_code=400, data=None):
        response_data = {
            "success": False,
            "statusCode": status_code,
            "message": message,
            "timestamp": timezone.now().isoformat()
        }
        
        if data is not None:
            response_data["data"] = data
            
        return Response(response_data, status=status_code)
