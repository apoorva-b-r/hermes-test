from functools import wraps
from flask import Flask, request, jsonify

app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header != "Bearer demo-admin-token":
            return jsonify({"error": "login required"}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.get("/admin/users")
@login_required
def get_admin_users():
    return jsonify([{"user": "placeholder"}]), 200


@app.get("/status")
def get_status():
    return jsonify({"ok": True}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 3003))
    app.run(host="0.0.0.0", port=port)

