from rest_framework.response import Response
import os, json

ERROR_MAP_PATH = os.path.join(os.path.dirname(__file__), "error_messages.json")

try:
    with open(ERROR_MAP_PATH, "r", encoding="utf-8") as f:
        ERROR_MESSAGES = json.load(f)
except FileNotFoundError:
    ERROR_MESSAGES = {}

def map_error_message(message: str) -> str:
    if not message:
        return "(warning) empty message"

    mapped = ERROR_MESSAGES.get(message)
    if mapped:
        return mapped
    else:
        return f"(new) {message}"


def success_response(status_code, message, data=None):   
    return Response({
        "success": True,
        "detail": message,
        "data": data or {}
    }, status=status_code)


def error_response(status_code, code, message):
    return Response({
        "success": False,
        "code": code,
        "detail": map_error_message(message)
    }, status=status_code)
