import os
import sqlite3
from flask import (
    Flask, request, jsonify, send_from_directory,
    render_template, redirect, url_for, session
)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

DB_PATH = os.path.join(app.root_path, "quote_bot.db")

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)
        c.execute("""
            CREATE TABLE quotes (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        c.execute("INSERT INTO users (username, password_hash) VALUES (?,?);",
                  ("admin", generate_password_hash("password123")))
        c.execute("INSERT INTO users (username, password_hash) VALUES (?,?);",
                  ("garyclayton2006", generate_password_hash("OnTime2025@")))
        conn.commit()
        conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quote", methods=["POST"])
def get_quote():
    data = request.get_json()
    name = data.get("name", "there")
    message = data.get("message", "")
    resp = f"Hey {name}, here's a quote based on your message: {message}"
    return jsonify({"response": resp, "email_status": "success"})

@app.route("/employee/quote", methods=["GET", "POST"])
def employee_quote():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        details = request.form["details"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO quotes (name, email, details) VALUES (?,?,?);",
            (name, email, details)
        )
        conn.commit()
        conn.close()
        return render_template("quote_submitted.html", name=name)
    return render_template("employee_quote.html")

@app.route("/admin/login", methods=["GET"])
def admin_login():
    return render_template("login.html")

@app.route("/admin/authenticate", methods=["POST"])
def admin_authenticate():
    username = request.form["username"]
    password = request.form["password"]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?;", (username,))
    row = c.fetchone()
    conn.close()

    if row and check_password_hash(row[0], password):
        session["user"] = username
        return redirect(url_for("admin_dashboard"))
    return render_template("login.html", error="Invalid credentials"), 401

@app.route("/admin/dashboard")
def admin_dashboard():
    if "user" not in session:
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, email, details, created_at FROM quotes ORDER BY created_at DESC;")
    quotes = c.fetchall()
    conn.close()
    return render_template("dashboard.html", user=session["user"], quotes=quotes)

@app.route("/admin/logout")
def admin_logout():
    session.pop("user", None)
    return redirect(url_for("admin_login"))

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
