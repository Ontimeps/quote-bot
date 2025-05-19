import os
from flask import Flask, request, jsonify, send_from_directory, render_template_string, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize app
app = Flask(__name__)
CORS(app)

# Secret key for session management (replace with a secure value in production)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Basic homepage
@app.route("/")
def index():
    return "Quote Bot is running."

# Chatbot /quote API
@app.route("/quote", methods=["POST"])
def get_quote():
    data = request.get_json()
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
                <input name="username" placeholder="Username" /><br><br>
                <input name="password" type="password" placeholder="Password" /><br><br>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
    """)

# Login POST route
@app.route("/admin/authenticate", methods=["POST"])
def admin_authenticate():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "password123":
        session["user"] = username
        return redirect(url_for("admin_dashboard"))
    else:
        return "Login failed. Try again.", 401

# Protected dashboard
@app.route("/admin/dashboard")
def admin_dashboard():
    if "user" in session:
        return f"<h2>Welcome to the admin dashboard, {session['user']}!</h2>"
    return redirect(url_for("admin_login"))

# Favicon
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


@app.route("/admin/logout")
def admin_logout():
    session.pop("user", None)
    return redirect(url_for("admin_login"))
@app.route("/admin/logout")
def admin_logout():
    session.pop("user", None)
    return redirect(url_for("admin_login"))
