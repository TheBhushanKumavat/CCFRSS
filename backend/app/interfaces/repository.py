from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.entities import EvaluatedTransaction

class TransactionRepository(ABC):
    @abstractmethod
    def save(self, evaluated_transaction: EvaluatedTransaction) -> None:
        pass

    @abstractmethod
    def get_by_id(self, transaction_id: str) -> Optional[EvaluatedTransaction]:
        pass

    @abstractmethod
    def get_all(self, limit: int = 100, skip: int = 0) -> List[EvaluatedTransaction]:
        pass

    @abstractmethod
    def clear_all(self) -> None:
        pass
