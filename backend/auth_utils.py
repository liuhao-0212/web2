from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request


def create_access_token(user_id: int, username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "iat": now,
        "exp": now + timedelta(days=7),
    }
    secret = current_app.config["SECRET_KEY"]
    token = jwt.encode(payload, secret, algorithm="HS256")
    if isinstance(token, bytes):
        return token.decode("utf-8")
    return token


def decode_token(token: str) -> dict:
    secret = current_app.config["SECRET_KEY"]
    return jwt.decode(token, secret, algorithms=["HS256"])


def require_auth(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "需要登录"}), 401
        raw = auth[7:].strip()
        if not raw:
            return jsonify({"error": "需要登录"}), 401
        try:
            data = decode_token(raw)
            g.user_id = int(data["sub"])
            g.username = data["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "登录已过期，请重新登录"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "无效的登录凭证"}), 401
        return f(*args, **kwargs)

    return wrapped
