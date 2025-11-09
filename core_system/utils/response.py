from rest_framework.response import Response
from rest_framework import status

def success_response(status_code, message, data=None):
    return Response({
        "success": True,
        "message": message,
        "data": data or {}
    }, status=status_code)

def error_response(status_code, detail, part, errors):
    return Response({
        "success": False,
        "detail": detail,
        "part": part,
        "errors": errors or {}
    }, status=status_code)
