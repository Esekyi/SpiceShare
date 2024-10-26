"""Providing google recaptcha verification service."""
import requests
from flask import current_app


def verify_recaptcha(recaptcha_response):
    """Verifies the Google reCAPTCHA response.
    
    Args:
        recaptcha_response (str): The token received from the frontend reCAPTCHA.

    Returns:
        bool: True if the verification is successful, False otherwise.
    """
    secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
    if not secret_key:
        raise ValueError(
            "RECAPTCHA_SECRET_KEY is missing in the configuration.")

    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify', data=data)

    if response.status_code == 200:
        result = response.json()
        return result.get('success', False)

    return False
