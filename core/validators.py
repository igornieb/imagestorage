from django.core.exceptions import ValidationError


def validate_time_allowed(value):
    # validates that values contains int only in range [300, 30000]
    value = int(value)
    if 300 <= value <= 30000:
        return value
    else:
        raise ValidationError("Value must be an integer in range [300, 30000]")
