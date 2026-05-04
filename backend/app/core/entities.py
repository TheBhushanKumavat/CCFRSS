from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Transaction(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique transaction ID")
    user_id: str = Field(..., description="ID of the user making the transaction")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="USD", description="Currency of the transaction")
    merchant_category: str = Field(..., description="Category of the merchant")
    merchant_location: str = Field(..., description="Location/Country of the merchant")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of transaction")
    
class FraudScore(BaseModel):
    transaction_id: str
    score: float = Field(..., ge=0.0, le=1.0, description="Fraud probability score (0.0 to 1.0)")
    risk_level: str = Field(..., description="Risk categorization (Low, Medium, High)")
    reasons: list[str] = Field(default_factory=list, description="Reasons for the given score")
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)

class EvaluatedTransaction(BaseModel):
    transaction: Transaction
    score: FraudScore
