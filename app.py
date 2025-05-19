import os
import json
from flask import Flask, request, jsonify, send_from_directory, render_template_string, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Secret key for sessions
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")

# Path to JSON user store
USERS_FILE = os.path.join(app.root_path, "users.json")

def load_users():
    """Load users from JSON file, creating default admin if necessary."""
    if not os.path.exists(USERS_FILE):
        default_pass = os.getenv("ADMIN_PASSWORD", "password123")
        default_hash = generate_password_hash(default_pass)
        with open(USERS_FILE, "w") as f:
            json.dump({"admin": default_hash}, f, indent=2)
    with open(USERS_FILE) as f:
        return json.load(f)

# Basic homepage
@app.route("/")
def index():
    return "Quote Bot is running."

# Chatbot /quote API
@app.route("/quote", methods=["POST"])
def get_quote():
    data = request.get_json() or {}
    name = data.get("name", "there")
    message = data.get("message", "")
    response = f"Hey {name}, here's a quote based on your message: {message}"
    return jsonify({"response": response, "email_status": "success"})

# Admin login form
@app.route("/admin/login")
def admin_login():
    return render_template_string("""
        <html>
        <head><title>Admin Login</title></head>
        <body style="font-family:sans-serif;">
            <h2>Admin Login</h2>
            <form action="/admin/authenticate" method="post">
                <input name="username" placeholder="Username" required><br><br>
                <input name="password" type="password" placeholder="Password" required><br><br>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
    """)

# Authenticate against JSON user store
@app.route("/admin/authenticate", methods=["POST"])
def admin_authenticate():
    users = load_users()
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    pw_hash = users.get(username)
    if pw_hash and check_password_hash(pw_hash, password):
        session["user"] = username
        return redirect(url_for("admin_dashboard"))
    return "Login failed. Try again.", 401

# Protected dashboard
@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("user"):
        return f"<h2>Welcome to the admin dashboard, {session['user']}!</h2>"
    return redirect(url_for("admin_login"))

# Logout endpoint
@app.route("/admin/logout")
def admin_logout():
    session.pop("user", None)
    return redirect(url_for("admin_login"))

# Favicon handler
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)