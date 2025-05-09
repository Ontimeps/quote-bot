import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

b64_creds = os.getenv("GOOGLE_CREDENTIALS_B64")
if not b64_creds:
    print("GOOGLE_CREDENTIALS_B64 not found.")
    exit()

decoded = base64.b64decode(b64_creds).decode("utf-8")
creds = json.loads(decoded)

print("📌 Service Account Info:")
print(f"Project ID     : {creds.get('project_id')}")
print(f"Client Email   : {creds.get('client_email')}")
print(f"Client ID      : {creds.get('client_id')}")
