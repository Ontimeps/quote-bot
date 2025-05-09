import pandas as pd

def generate_quote(message):
    df = pd.read_csv("large_format_price_sheet_shopvox.csv")
    # Simplified logic — replace with real parsing
    if "10ft" in message.lower():
        return "You're looking at roughly $100–$200 for a 10ft banner."
    return "Please provide more details for an accurate quote."
