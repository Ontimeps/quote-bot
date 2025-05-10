import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route("/")
def home():
    return "Quote Bot is running."

@app.route("/quote", methods=["POST"])
def quote():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    message = data.get("message")
    name = data.get("name")
    email = data.get("email")

    if not message or not name or not email:
        return jsonify({"error": "Missing required fields"}), 400

    # Example response
    response = f"Hello {name}, thank you for your quote request!"
    return jsonify({"email_status": "mocked", "response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
