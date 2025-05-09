import os
app = Flask(__name__)
CORS(app)

setup_routes(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
