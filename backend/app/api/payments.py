from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class PaymentRequest(BaseModel):
    order_id: int
    payment_method: str = "balance"

class PaymentResponse(BaseModel):
    status: str
    transaction_id: str

@router.post("/pay", response_model=PaymentResponse)
async def process_payment(request: PaymentRequest):
    # TODO: Implement payment processing
    return {"status": "success", "transaction_id": "tx_001"}
