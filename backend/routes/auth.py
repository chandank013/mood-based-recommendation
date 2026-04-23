"""
Auth routes — JWT-based authentication.

POST /api/auth/register  — create account
POST /api/auth/login     — get JWT token
POST /api/auth/logout    — client-side token removal (stateless)
GET  /api/auth/me        — get current user info
"""
import re
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from db.connection import execute, execute_write
from config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _generate_token(user_id: int, username: str, email: str) -> str:
    payload = {
        "user_id"  : user_id,
        "username" : username,
        "email"    : email,
        "exp"      : datetime.now(timezone.utc) + timedelta(days=7),
        "iat"      : datetime.now(timezone.utc),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")


def _decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def _get_token_from_request() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return request.cookies.get("token")


# ── Auth decorator ────────────────────────────────────────────────────────────

def login_required(f):
    """Decorator — rejects request if no valid JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_token_from_request()
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        payload = _decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated


def optional_auth(f):
    """Decorator — attaches user if token present, continues if not."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_token_from_request()
        if token:
            payload = _decode_token(token)
            request.user = payload  # None if invalid
        else:
            request.user = None
        return f(*args, **kwargs)
    return decorated


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    data     = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    # Validation
    if not username or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400
    if len(username) < 3 or len(username) > 50:
        return jsonify({"error": "Username must be 3–50 characters"}), 400
    if not re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", email):
        return jsonify({"error": "Invalid email address"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Check existing
    existing = execute(
        "SELECT id FROM users WHERE email=%s OR username=%s LIMIT 1",
        (email, username), fetchone=True
    )
    if existing:
        return jsonify({"error": "Email or username already registered"}), 409

    # Create user
    password_hash = _hash_password(password)
    user_id = execute_write(
        "INSERT INTO users (username, email, password_hash) VALUES (%s,%s,%s)",
        (username, email, password_hash)
    )

    token = _generate_token(user_id, username, email)

    return jsonify({
        "message" : "Account created successfully",
        "token"   : token,
        "user"    : {"id": user_id, "username": username, "email": email},
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json(force=True)
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = execute(
        "SELECT id, username, email, password_hash FROM users WHERE email=%s LIMIT 1",
        (email,), fetchone=True
    )

    if not user or not _check_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password"}), 401

    # Update last login
    execute_write("UPDATE users SET last_login=NOW() WHERE id=%s", (user["id"],))

    token = _generate_token(user["id"], user["username"], user["email"])

    return jsonify({
        "message" : "Login successful",
        "token"   : token,
        "user"    : {
            "id"      : user["id"],
            "username": user["username"],
            "email"   : user["email"],
        },
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    # JWT is stateless — client just deletes the token
    return jsonify({"message": "Logged out successfully"})


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    user_id = request.user["user_id"]
    user = execute(
        "SELECT id, username, email, created_at, last_login FROM users WHERE id=%s",
        (user_id,), fetchone=True
    )
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get mood stats
    stats = execute(
        """SELECT COUNT(*) as total_moods,
                  MAX(created_at) as last_mood
           FROM mood_logs WHERE user_id=%s""",
        (user_id,), fetchone=True
    )

    return jsonify({
        "user": {
            "id"          : user["id"],
            "username"    : user["username"],
            "email"       : user["email"],
            "created_at"  : str(user["created_at"]),
            "last_login"  : str(user["last_login"]),
            "total_moods" : stats["total_moods"] if stats else 0,
            "last_mood"   : str(stats["last_mood"]) if stats and stats["last_mood"] else None,
        }
    })