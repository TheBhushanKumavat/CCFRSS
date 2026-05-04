import sqlite3
import json
from typing import List, Optional
from app.core.entities import EvaluatedTransaction, Transaction, FraudScore
from app.interfaces.repository import TransactionRepository

class SQLiteTransactionRepository(TransactionRepository):
    def __init__(self, db_path: str = "transactions.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluated_transactions (
                    id TEXT PRIMARY KEY,
                    transaction_data TEXT NOT NULL,
                    score_data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save(self, evaluated_transaction: EvaluatedTransaction) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Use the transaction id, or generate one if None (should be assigned by use case)
            t_id = evaluated_transaction.transaction.id
            
            cursor.execute(
                "INSERT OR REPLACE INTO evaluated_transactions (id, transaction_data, score_data) VALUES (?, ?, ?)",
                (
                    t_id,
                    evaluated_transaction.transaction.model_dump_json(),
                    evaluated_transaction.score.model_dump_json()
                )
            )
            conn.commit()

    def get_by_id(self, transaction_id: str) -> Optional[EvaluatedTransaction]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT transaction_data, score_data FROM evaluated_transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()
            if row:
                t_data = json.loads(row[0])
                s_data = json.loads(row[1])
                return EvaluatedTransaction(
                    transaction=Transaction(**t_data),
                    score=FraudScore(**s_data)
                )
        return None

    def get_all(self, limit: int = 100, skip: int = 0) -> List[EvaluatedTransaction]:
        results = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT transaction_data, score_data FROM evaluated_transactions ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, skip)
            )
            rows = cursor.fetchall()
            for row in rows:
                t_data = json.loads(row[0])
                s_data = json.loads(row[1])
                results.append(EvaluatedTransaction(
                    transaction=Transaction(**t_data),
                    score=FraudScore(**s_data)
                ))
        return results

    def clear_all(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evaluated_transactions")
            conn.commit()
