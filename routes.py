from flask import request, jsonify
from utils.emailer import send_email
from utils.logger import log_msg
from utils.price_calc import generate_quote

def setup_routes(app):
    @app.route('/quote', methods=['POST'])
    def quote():
        data = request.get_json()
        name = data.get('name', 'User')
        message = data.get('message', '')
        email = data.get('email', '')

        reply = generate_quote(message)
        try:
            send_email(name, email, message, reply)
            email_status = "sent"
        except Exception as e:
            print(f"Email Error: {e}")
            email_status = "failed"

        log_msg("web", name, message, reply, email_status)
        return jsonify({'response': reply, 'email_status': email_status})
