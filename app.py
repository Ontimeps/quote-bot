# app.py
import os
import json
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")

USERS_FILE = os.path.join(app.root_path, "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        default_pass = os.getenv("ADMIN_PASSWORD", "password123")
        with open(USERS_FILE, "w") as f:
            json.dump({"admin": generate_password_hash(default_pass)}, f, indent=2)
    with open(USERS_FILE) as f:
        return json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quote", methods=["POST"])
def get_quote():
    data = request.get_json() or {}
    name = data.get("name", "there")
    message = data.get("message", "")
    return jsonify({
        "response": f"Hey {name}, here's a quote based on your message: {message}",
        "email_status": "success"
    })

@app.route("/admin/login")
def admin_login():
    return render_template("login.html")

@app.route("/admin/authenticate", methods=["POST"])
def admin_authenticate():
    users = load_users()
    user = request.form.get("username", "")
    pw = request.form.get("password", "")
    pw_hash = users.get(user)
    if pw_hash and check_password_hash(pw_hash, pw):
        session["user"] = user
        return redirect(url_for("admin_dashboard"))
    return "Login failed. Try again.", 401

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("user"):
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("admin_login"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("user", None)
    return redirect(url_for("admin_login"))

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)