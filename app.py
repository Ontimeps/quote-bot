import os
import sqlite3
from datetime import datetime
from flask import (
    Flask, request, jsonify, send_from_directory,
    render_template, redirect, url_for, session
)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import openai

# Configure OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# SQLite DB setup
DB_PATH = os.path.join(app.root_path, "quotes.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute(@"
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        customer TEXT,
        contact TEXT,
        details TEXT,
        estimate TEXT
    )
"@)
conn.commit()

# Home page with motivational quotes
MOTIVATIONAL = [
    "Your limitation - it's only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn't just find you. You have to go out and get it."
]

@app.route("/")
def index():
    quote = random.choice(MOTIVATIONAL)
    return render_template("index.html", quote=quote)

# API endpoint
@app.route("/quote", methods=["POST"])
def get_quote():
    data = request.get_json() or {}
    name = data.get("name", "there")
    message = data.get("message", "")
    resp = f"Hey {name}, here's a quote based on your message: {message}"
    return jsonify({"response": resp, "email_status": "success"})

# Employee-facing quote form with GPT pricing
@app.route("/employee/quote", methods=["GET","POST"])
def employee_quote():
    quote_text = None
    if request.method == "POST":
        customer = request.form.get("customer","Customer")
        contact  = request.form.get("contact","")
        details  = request.form.get("details","")
        # Call GPT to generate an estimate
        system = "You are a pricing engine. Given job details, respond ONLY with a price estimate in USD, no extra commentary."
        user = f"Calculate a realistic price in USD for the following job details: '{details}'."
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":system},
                {"role":"user","content":user}
            ],
            temperature=0.2,
            max_tokens=50
        )
        estimate = resp.choices[0].message.content.strip()
        timestamp = datetime.utcnow().isoformat()
        # Save to SQLite
        c.execute(
            "INSERT INTO quotes (timestamp, customer, contact, details, estimate) VALUES (?,?,?,?,?)",
            (timestamp, customer, contact, details, estimate)
        )
        conn.commit()
        quote_text = f"Quote for {customer} ({contact}): {estimate}"
    return render_template("employee_quote.html", quote=quote_text)

# Employee history page
@app.route("/employee/history")
def employee_history():
    c.execute("SELECT timestamp, customer, contact, details, estimate FROM quotes ORDER BY id DESC")
    rows = c.fetchall()
    return render_template("employee_history.html", quotes=rows)

# Admin login/auth
@app.route("/admin/login")
def admin_login():
    return render_template("login.html")

@app.route("/admin/authenticate", methods=["POST"])
def admin_authenticate():
    # simple in-memory admin user
    user = request.form.get("username","")
    pw   = request.form.get("password","")
    if user=="admin" and check_password_hash(generate_password_hash(os.getenv("ADMIN_PASSWORD","password123")), pw):
        session["user"] = "admin"
        return redirect(url_for("admin_dashboard"))
    return render_template("login.html", error="Login failed"),401

@app.route("/admin/dashboard")
def admin_dashboard():
    if "user" not in session:
        return redirect(url_for("admin_login"))
    c.execute("SELECT id, customer, contact, details, estimate, timestamp FROM quotes ORDER BY id DESC")
    data = c.fetchall()
    return render_template("dashboard.html", quotes=data)

@app.route("/admin/logout")
def admin_logout():
    session.pop("user",None)
    return redirect(url_for("admin_login"))

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path,"static"),"favicon.ico",mimetype="image/vnd.microsoft.icon")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)
