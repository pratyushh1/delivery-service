import os
import requests
from app.schemas import OrderDTO

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8082")


def get_order(order_id: str) -> OrderDTO | None:
    """Calls order-service over REST to confirm an order exists.
    delivery-service never reads order-service's database directly.
    """
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/orders/{order_id}", timeout=5)
    except requests.RequestException as e:
        raise RuntimeError(f"Could not reach order-service: {e}") from e

    if response.status_code == 404:
        return None
    response.raise_for_status()
    return OrderDTO(**response.json())
