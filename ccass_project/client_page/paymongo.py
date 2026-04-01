import base64
import requests
from django.conf import settings

PAYMONGO_BASE_URL = "https://api.paymongo.com/v1"


def _auth_header():
    """Return headers with basic auth for PayMongo API"""
    key = f"{settings.PAYMONGO_SECRET_KEY}:"
    encoded = base64.b64encode(key.encode()).decode()

    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json"
    }


def create_payment_intent(amount):
    """
    Create a PayMongo payment intent.
    Amount should be in centavos (integer).
    """
    amount = int(amount)

    response = requests.post(
        f"{PAYMONGO_BASE_URL}/payment_intents",
        headers=_auth_header(),
        json={
            "data": {
                "attributes": {
                    "amount": amount,
                    "currency": "PHP",
                    "payment_method_allowed": ["card"],
                    "capture_type": "automatic"
                }
            }
        }
    )

    print("=== CREATE PAYMENT INTENT ===")
    print("Status Code:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()
    return response.json()


def attach_payment_method(intent_id, payment_method_id):
    """
    Attach a payment method to a payment intent (card-safe, 3DS-ready).
    """

    response = requests.post(
        f"{PAYMONGO_BASE_URL}/payment_intents/{intent_id}/attach",
        headers=_auth_header(),
        json={
            "data": {
                "attributes": {
                    # ✅ MUST be a STRING (not an object)
                    "payment_method": payment_method_id,

                    # ✅ REQUIRED for card / 3DS
                    "return_url": settings.PAYMONGO_RETURN_URL
                }
            }
        }
    )

    print("=== ATTACH PAYMENT METHOD ===")
    print("Intent ID:", intent_id)
    print("Payment Method ID:", payment_method_id)
    print("Status Code:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()
    return response.json()
