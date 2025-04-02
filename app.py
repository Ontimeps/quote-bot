import os
import json
import openai
import sqlite3
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
from email.mime.text import MIMEText
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# Twilio setup
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Gmail API setup
creds = service_account.Credentials.from_service_account_info(
    json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON")),
    scopes=["https://www.googleapis.com/auth/gmail.send"]
)
gmail_service = build("gmail", "v1", credentials=creds)

# Admin token
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin123")

# SQLite setup
conn = sqlite3.connect("quotes.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    sender TEXT,
    message TEXT,
    response TEXT,
    timestamp TEXT
)
''')
conn.commit()

# Load pricing data
price_df = pd.read_csv("large_format_price_sheet_shopvox.csv")

def log_msg(source, sender, message, response):
    cursor.execute("INSERT INTO logs (source, sender, message, response, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (source, sender, message, response, datetime.now().isoformat()))
    conn.commit()

def generate_quote_response(message):
    prompt = f"""
Act as a friendly and professional print shop assistant (lightly witty). A customer said: "{message}". Based on the price list and general tone, respond naturally with a helpful price range and suggestions. Don't sound robotic.

Example:
"Hey there! For a full wrap on an SUV, you'd be looking around $2,500 to $4,500 depending on finish and install. Want me to pencil in a mock-up or quote?"

Now go:
"""
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message["content"]

@app.route("/quote", methods=["POST"])
def quote():
    data = request.json
    message = data.get("message", "")
    sender = data.get("name", "web")
    email = data.get("email")

    reply = generate_quote_response(message)
    log_msg("web", sender, message, reply)

    if email:
        send_email(email, "Your Quote from KC Signs", reply)

    return jsonify({"response": reply})

@app.route("/sms", methods=["POST"])
def sms():
    msg = request.form.get("Body")
    sender = request.form.get("From")
    reply = generate_quote_response(msg)
    log_msg("sms", sender, msg, reply)
    twiml = MessagingResponse()
    twiml.message(reply)
    return str(twiml)

@app.route("/call", methods=["POST"])
def call():
    r = VoiceResponse()
    r.say("Thanks for calling KC Signs! Tell me what you need a quote for—like a banner or a vehicle wrap—and I’ll text you back with pricing!", voice="Polly.Joanna")
    return str(r)

@app.route("/admin", methods=["GET"])
def admin():
    token = request.args.get("token")
    if token != ADMIN_TOKEN:
        return "Unauthorized", 403

    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    html = '''
    <h1>Quote Logs</h1>
    <table border="1">
    <tr><th>ID</th><th>Source</th><th>Sender</th><th>Message</th><th>Response</th><th>Timestamp</th></tr>
    {% for r in rows %}
    <tr><td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td><td>{{r[3]}}</td><td>{{r[4]}}</td><td>{{r[5]}}</td></tr>
    {% endfor %}
    </table>
    '''
    return render_template_string(html, rows=rows)

def send_email(to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = {'raw': message.as_bytes().decode('utf-8')}
    gmail_service.users().messages().send(userId="me", body=raw).execute()

@app.route("/")
def home():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
