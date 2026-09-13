from rest_framework.response import Response
from rest_framework import status

def api_response(data=None, message="Success", status_code=status.HTTP_200_OK, errors=None):
    payload = {
        "success": status_code < 400,
        "message": message,
        "data": data,
        "errors": errors
    }
    return Response(payload, status=status_code)
