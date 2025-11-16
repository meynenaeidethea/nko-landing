# auth.py (обновленная версия)
from flask import Blueprint, request, jsonify, current_app
from backend.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import secrets
from backend.config import Config
from backend.utils.validators import validate_email

auth_bp = Blueprint('auth', __name__)

# Хранилище для токенов сброса пароля (в продакшене использовать Redis)
password_reset_tokens = {}

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Проверяем обязательные поля
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email и пароль обязательны'}), 400
        
        # Валидация email
        if not validate_email(data['email']):
            return jsonify({'error': 'Некорректный формат email'}), 400
        
        # Проверяем уникальность email
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Пользователь с таким email уже существует'}), 409
        
        # Проверяем длину пароля
        if len(data['password']) < 6:
            return jsonify({'error': 'Пароль должен содержать минимум 6 символов'}), 400
        
        # Создаем нового пользователя
        new_user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_admin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Создаем JWT токен
        token = jwt.encode({
            'user_id': new_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'is_admin': new_user.is_admin
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email и пароль обязательны'}), 400
        
        # Ищем пользователя
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        # Проверяем пароль
        if not check_password_hash(user.password, data['password']):
            return jsonify({'error': 'Неверный пароль'}), 401
        
        # Создаем JWT токен
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email обязателен'}), 400
        
        user = User.query.filter_by(email=email).first()
        if user:
            # Генерируем токен сброса пароля
            reset_token = secrets.token_urlsafe(32)
            password_reset_tokens[reset_token] = {
                'user_id': user.id,
                'expires': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            
            # В реальном приложении здесь должна быть отправка email
            # Для демо просто возвращаем токен
            return jsonify({
                'message': 'Инструкции по сбросу пароля отправлены на email',
                'reset_token': reset_token  # В продакшене не возвращать!
            }), 200
        else:
            # Для безопасности не сообщаем, что пользователь не найден
            return jsonify({'message': 'Если email зарегистрирован, инструкции будут отправлены'}), 200
            
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'error': 'Токен и новый пароль обязательны'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Пароль должен содержать минимум 6 символов'}), 400
        
        # Проверяем токен
        token_data = password_reset_tokens.get(token)
        if not token_data:
            return jsonify({'error': 'Неверный или просроченный токен'}), 400
        
        if datetime.datetime.utcnow() > token_data['expires']:
            del password_reset_tokens[token]
            return jsonify({'error': 'Токен истек'}), 400
        
        user = User.query.get(token_data['user_id'])
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        # Обновляем пароль
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        # Удаляем использованный токен
        del password_reset_tokens[token]
        
        return jsonify({'message': 'Пароль успешно изменен'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Токен отсутствует'}), 401
        
        token = token[7:]  # Убираем 'Bearer '
        
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin
            }
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Токен истек'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Неверный токен'}), 401
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Токен отсутствует'}), 401
        
        token = token[7:]
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Текущий и новый пароль обязательны'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Новый пароль должен содержать минимум 6 символов'}), 400
        
        if not check_password_hash(user.password, current_password):
            return jsonify({'error': 'Неверный текущий пароль'}), 401
        
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Пароль успешно изменен'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Токен истек'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Неверный токен'}), 401
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500