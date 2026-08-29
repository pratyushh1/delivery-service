from pydantic import BaseModel


class DeliveryCreate(BaseModel):
    order_id: str
    partner_name: str


class DeliveryOut(BaseModel):
    id: str
    order_id: str
    partner_name: str
    status: str


# Mirrors the shape of order-service's Order, as returned over REST.
# delivery-service never touches order-service's database directly.
class OrderDTO(BaseModel):
    id: str
    restaurant_id: str
    item_id: str
    quantity: int
    total_price: float
    status: str
