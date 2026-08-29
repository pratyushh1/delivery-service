from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise ValueError(f"'{id_str}' is not a valid id")


def serialize_delivery(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "order_id": doc["order_id"],
        "partner_name": doc["partner_name"],
        "status": doc["status"],
    }
