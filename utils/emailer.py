import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
from email.message import EmailMessage

def send_email(name, to_email, user_msg, response):
    service = _build_gmail_service()
    msg = EmailMessage()
    msg.set_content(f"Hi {name},\n\n{response}\n\nOriginal message:\n{user_msg}")
    msg['To'] = to_email
    msg['From'] = 'you@example.com'
    msg['Subject'] = 'Your Quote'

    raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={'raw': raw_msg}).execute()

def _build_gmail_service():
    creds_json = base64.b64decode(os.getenv("GOOGLE_CREDENTIALS_B64")).decode()
    creds = service_account.Credentials.from_service_account_info(eval(creds_json), scopes=['https://www.googleapis.com/auth/gmail.send'])
    return build('gmail', 'v1', credentials=creds)
