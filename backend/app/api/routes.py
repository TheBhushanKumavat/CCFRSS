from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
import csv
import io

from typing import List
from app.core.entities import Transaction, EvaluatedTransaction
from app.core.use_cases import FraudScoringUseCase
from app.infrastructure.sqlite_repository import SQLiteTransactionRepository
from app.infrastructure.mock_ml_model import MockFraudModel

router = APIRouter()

# Dependency Injection
def get_use_case():
    repository = SQLiteTransactionRepository()
    model = MockFraudModel()
    return FraudScoringUseCase(repository=repository, model=model)

@router.post("/evaluate", response_model=EvaluatedTransaction)
async def evaluate_transaction(
    transaction: Transaction,
    use_case: FraudScoringUseCase = Depends(get_use_case)
):
    return use_case.execute(transaction)

@router.get("/transactions", response_model=List[EvaluatedTransaction])
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    use_case: FraudScoringUseCase = Depends(get_use_case)
):
    return use_case.repository.get_all(limit=limit, skip=skip)

@router.post("/evaluate/batch", response_model=List[EvaluatedTransaction])
async def evaluate_batch(
    file: UploadFile = File(...),
    use_case: FraudScoringUseCase = Depends(get_use_case)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported for batch evaluation.")
    
    contents = await file.read()
    decoded = contents.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    evaluated_transactions = []
    
    for row in reader:
        try:
            tx = Transaction(
                user_id=row['user_id'],
                amount=float(row['amount']),
                currency=row.get('currency', 'USD'),
                merchant_category=row['merchant_category'],
                merchant_location=row['merchant_location']
            )
            result = use_case.execute(tx)
            evaluated_transactions.append(result)
        except Exception as e:
            # Skip invalid rows or handle them appropriately
            pass
            
    return evaluated_transactions

@router.delete("/transactions/clear")
async def clear_transactions(use_case: FraudScoringUseCase = Depends(get_use_case)):
    use_case.repository.clear_all()
    return {"message": "All transactions have been cleared successfully."}

