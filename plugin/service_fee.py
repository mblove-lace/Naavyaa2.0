from decimal import Decimal

def calculate_service_fee(order_total):
    # Example service fee calculation (10% of order total)
    service_fee = 5  # Flat fee for simplicity, can be modified to be percentage-based
    return Decimal(order_total)* Decimal (service_fee) / 100
