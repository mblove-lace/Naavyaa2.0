# from decimal import Decimal
# from requests import get

# def fetch_exchange_rate(base_currency: str, target_currency: str) -> Decimal:
#     """
#     Fetches the exchange rate from base_currency to target_currency using an external API.
    
#     Args:
#         base_currency (str): The currency code of the base currency (e.g., 'USD').
#         target_currency (str): The currency code of the target currency (e.g., 'EUR').
    
#     Returns:
#         Decimal: The exchange rate from base_currency to target_currency.
#     """
#     api_url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
#     response = get(api_url)
    
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch exchange rates: {response.status_code}")
    
#     data = response.json()
    
#     if target_currency not in data['rates']:
#         raise Exception(f"Target currency '{target_currency}' not found in exchange rates.")
    
#     return Decimal(data['rates']['INR'])