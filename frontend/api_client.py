import requests
from typing import Dict, Any, List

LIVE_API_BASE_URL = "https://ccfrss-backend.onrender.com/api/v1"
API_BASE_URL = "http://localhost:8000/api/v1"


def evaluate_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{API_BASE_URL}/evaluate", json=transaction_data)
    response.raise_for_status()
    return response.json()

def get_transactions() -> List[Dict[str, Any]]:
    response = requests.get(f"{API_BASE_URL}/transactions")
    response.raise_for_status()
    return response.json()

def evaluate_batch(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
    files = {'file': (filename, file_content, 'text/csv')}
    response = requests.post(f"{API_BASE_URL}/evaluate/batch", files=files)
    response.raise_for_status()
    return response.json()

def clear_transactions() -> Dict[str, Any]:
    response = requests.delete(f"{API_BASE_URL}/transactions/clear")
    response.raise_for_status()
    return response.json()
