from flask import Blueprint, request, jsonify
from backend.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 400

    hashed = generate_password_hash(password)
    user = User(email=email, password=hashed, is_admin=False)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "registered"})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "invalid credentials"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"error": "invalid credentials"}), 401

    return jsonify({
        "message": "logged in",
        "user_id": user.id,
        "is_admin": user.is_admin
    })
