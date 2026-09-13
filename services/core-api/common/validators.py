from django.core.exceptions import ValidationError
import re

def validate_phone_number(value):
    pattern = r'^\+?[1-9]\d{1,14}$'
    if not re.match(pattern, value):
        raise ValidationError("Phone number must be entered in E.164 format (e.g. +14155552671).")

def validate_positive_amount(value):
    if value <= 0:
        raise ValidationError("Amount must be strictly positive.")
