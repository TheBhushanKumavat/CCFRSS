from abc import ABC, abstractmethod
from app.core.entities import Transaction, FraudScore

class FraudDetectionModel(ABC):
    @abstractmethod
    def evaluate(self, transaction: Transaction) -> FraudScore:
        pass
