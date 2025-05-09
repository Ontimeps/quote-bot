import base64

with open("quote-bot-gmail.json", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
    print(b64)
