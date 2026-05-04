from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from auth_utils import create_access_token, require_auth
from extensions import db
from models import User
from routes import bp


def _validate_username(u: str) -> bool:
    return 3 <= len(u) <= 64 and u == u.strip()


@bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not _validate_username(username):
        return jsonify({"error": "用户名需为 3～64 个字符"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码至少 6 位"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "该用户名已被注册"}), 409

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(user.id, user.username)
    return (
        jsonify({"token": token, "user": {"id": user.id, "username": user.username}}),
        201,
    )


@bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error": "请输入用户名和密码"}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "用户名或密码错误"}), 401

    token = create_access_token(user.id, user.username)
    return jsonify({"token": token, "user": {"id": user.id, "username": user.username}})


@bp.route("/auth/me", methods=["GET"])
@require_auth
def me():
    return jsonify(
        {"user": {"id": g.user_id, "username": g.username}}
    )


@bp.route("/auth/logout", methods=["POST"])
def logout():
    """JWT 无状态；前端删除 token 即可。此处占位便于扩展黑名单。"""
    return jsonify({"ok": True})
