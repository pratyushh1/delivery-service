from fastapi import FastAPI, HTTPException
from pymongo.errors import PyMongoError
import time

from app.database import deliveries_collection, client as mongo_client
from app import schemas, client
from app.utils import to_object_id, serialize_delivery

VALID_STATUSES = {"ASSIGNED", "OUT_FOR_DELIVERY", "DELIVERED"}

app = FastAPI(title="delivery-service")


@app.on_event("startup")
def on_startup():
    last_error = None
    for attempt in range(10):
        try:
            mongo_client.admin.command("ping")
            return
        except PyMongoError as e:
            last_error = e
            time.sleep(3)
    raise RuntimeError(f"Could not connect to MongoDB after retries: {last_error}")


@app.get("/health")
def health():
    return {"status": "delivery-service is up"}


@app.post("/deliveries", response_model=schemas.DeliveryOut)
def create_delivery(request: schemas.DeliveryCreate):
    # Confirm the order exists by calling order-service over HTTP.
    try:
        order = client.get_order(request.order_id)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if order is None:
        raise HTTPException(status_code=400, detail=f"Order {request.order_id} not found")
    if order.status != "PLACED":
        raise HTTPException(status_code=400, detail=f"Order {request.order_id} is not in PLACED status")

    delivery_doc = {
        "order_id": request.order_id,
        "partner_name": request.partner_name,
        "status": "ASSIGNED",
    }
    result = deliveries_collection.insert_one(delivery_doc)
    doc = deliveries_collection.find_one({"_id": result.inserted_id})
    return serialize_delivery(doc)


@app.put("/deliveries/{delivery_id}/status", response_model=schemas.DeliveryOut)
def update_status(delivery_id: str, status: str):
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(VALID_STATUSES)}")

    try:
        oid = to_object_id(delivery_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = deliveries_collection.find_one_and_update(
        {"_id": oid}, {"$set": {"status": status}}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return serialize_delivery(result)


@app.get("/deliveries", response_model=list[schemas.DeliveryOut])
def list_deliveries():
    return [serialize_delivery(doc) for doc in deliveries_collection.find()]


@app.get("/deliveries/{delivery_id}", response_model=schemas.DeliveryOut)
def get_delivery(delivery_id: str):
    try:
        oid = to_object_id(delivery_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = deliveries_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return serialize_delivery(doc)
