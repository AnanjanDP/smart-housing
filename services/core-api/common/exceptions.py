from rest_framework.exceptions import APIException
from rest_framework import status

class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, please try again later.'
    default_code = 'service_unavailable'

class ResourceNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'

class ValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input parameters.'
    default_code = 'validation_error'
