from app.core.entities import Transaction, EvaluatedTransaction
from app.interfaces.repository import TransactionRepository
from app.interfaces.ml_model import FraudDetectionModel
import uuid

class FraudScoringUseCase:
    def __init__(self, repository: TransactionRepository, model: FraudDetectionModel):
        self.repository = repository
        self.model = model

    def execute(self, transaction: Transaction) -> EvaluatedTransaction:
        # Assign a unique ID if not present
        if not transaction.id:
            transaction.id = str(uuid.uuid4())

        # Evaluate the transaction using the model
        score = self.model.evaluate(transaction)
        
        # Ensure the score has the same transaction ID
        score.transaction_id = transaction.id

        evaluated_txn = EvaluatedTransaction(
            transaction=transaction,
            score=score
        )

        # Save the result to the repository
        self.repository.save(evaluated_txn)

        return evaluated_txn
