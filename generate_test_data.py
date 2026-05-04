import csv
import random
import uuid
import os

NUM_TRANSACTIONS = 100
OUTPUT_FILE = "test_transactions.csv"

# Pre-defined data lists
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "INR"]
CATEGORIES = ["Retail", "Groceries", "Electronics", "Travel", "Crypto", "Gambling", "Restaurant", "Wire Transfer", "Other"]
LOCATIONS = ["New York, USA", "London, UK", "Mumbai, India", "Tokyo, Japan", "Paris, France", "Country_X", "HighRisk_Island"]

def generate_transaction():
    """Generates a single randomized transaction with some patterns to trigger risk rules."""
    
    # 10% chance to be a high-risk transaction profile
    is_high_risk = random.random() < 0.10
    
    if is_high_risk:
        # High risk characteristics: large amount, risky categories, or risky locations
        amount = round(random.uniform(5000, 50000), 2)
        category = random.choice(["Crypto", "Gambling", "Wire Transfer"])
        location = random.choice(["Country_X", "HighRisk_Island", "Unknown"])
    else:
        # Normal risk characteristics
        amount = round(random.uniform(5, 500), 2)
        category = random.choice(["Retail", "Groceries", "Restaurant", "Electronics", "Other"])
        location = random.choice(["New York, USA", "London, UK", "Mumbai, India", "Tokyo, Japan", "Paris, France"])

    return {
        "user_id": f"user_{random.randint(1000, 9999)}",
        "amount": amount,
        "currency": random.choice(CURRENCIES),
        "merchant_category": category,
        "merchant_location": location
    }

def generate_csv():
    print(f"Generating {NUM_TRANSACTIONS} randomized transactions...")
    
    file_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "amount", "currency", "merchant_category", "merchant_location"])
        writer.writeheader()
        
        for _ in range(NUM_TRANSACTIONS):
            writer.writerow(generate_transaction())
            
    print(f"✅ Successfully created '{OUTPUT_FILE}' with {NUM_TRANSACTIONS} records.")

if __name__ == "__main__":
    generate_csv()
