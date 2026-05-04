from app.core.entities import Transaction, FraudScore
from app.interfaces.ml_model import FraudDetectionModel
import random

class MockFraudModel(FraudDetectionModel):
    def evaluate(self, transaction: Transaction) -> FraudScore:
        score = 0.1 # base score
        reasons = []

        # High amount rule
        if transaction.amount > 5000:
            score += 0.4
            reasons.append("Unusually high transaction amount.")
        elif transaction.amount > 1000:
            score += 0.15
            reasons.append("High transaction amount.")

        # Risky category rule
        risky_categories = ['Crypto', 'Gambling', 'Wire Transfer']
        if any(cat.lower() in transaction.merchant_category.lower() for cat in risky_categories):
            score += 0.3
            reasons.append("Merchant category is considered high-risk.")

        # Risky location rule
        risky_locations = ['Country_X', 'Country_Y', 'Unknown']
        if any(loc.lower() in transaction.merchant_location.lower() for loc in risky_locations):
            score += 0.3
            reasons.append("Transaction originated from a high-risk location.")

        # Add some randomness to simulate ML confidence/uncertainty
        score += random.uniform(-0.05, 0.1)

        # Clamp score between 0.0 and 1.0
        score = max(0.0, min(1.0, score))

        if score > 0.75:
            risk_level = "High"
        elif score > 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            if not reasons:
                reasons.append("Transaction appears normal.")

        return FraudScore(
            transaction_id=transaction.id or "unknown",
            score=round(score, 4),
            risk_level=risk_level,
            reasons=reasons
        )
