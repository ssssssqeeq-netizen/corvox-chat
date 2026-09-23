import sqlite3
import random
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import (get_db_connection, is_email_taken, is_tag_taken,
                     update_user_profile, get_user_by_id)
from mailer import send_verification_code

auth_bp = Blueprint('auth', __name__)

pending_codes = {}

@auth_bp.route('/check', methods=['POST'])
def check_availability():
    data = request.json
    email = data.get('email')
    tag = data.get('tag')
    result = {'email_taken': False, 'tag_taken': False}
    if email: result['email_taken'] = is_email_taken(email)
    if tag: result['tag_taken'] = is_tag_taken(tag)
    return jsonify(result), 200

@auth_bp.route('/send-code', methods=['POST'])
def send_code():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Введите email'}), 400
    code = str(random.randint(100000, 999999))
    pending_codes[email] = code
    print(f"\n[ОТЛАДКА] Код для {email}: {code}\n")
    success, message = send_verification_code(email, code)
    if success:
        return jsonify({'message': 'Код отправлен на вашу почту'}), 200
    else:
        return jsonify({'error': f'Не удалось отправить письмо: {message}'}), 500

@auth_bp.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    if not email or not code:
        return jsonify({'error': 'Введите код'}), 400
    saved = pending_codes.get(email)
    if saved and saved == code:
        del pending_codes[email]
        return jsonify({'message': 'Код подтверждён'}), 200
    else:
        return jsonify({'error': 'Неверный код. Попробуйте снова.'}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    tag = data.get('tag')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'error': 'Почта, имя и пароль обязательны для заполнения.'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Пароль должен содержать минимум 8 символов.'}), 400

    password_hash = generate_password_hash(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (email, name, tag, password_hash) VALUES (?, ?, ?, ?)',
            (email, name, tag, password_hash)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Регистрация прошла успешно!'}), 201
    except sqlite3.IntegrityError:
        if is_email_taken(email): return jsonify({'error': 'Этот email уже зарегистрирован в системе.'}), 400
        elif tag and is_tag_taken(tag): return jsonify({'error': 'Этот тег уже занят. Пожалуйста, выберите другой.'}), 400
        else: return jsonify({'error': 'Пользователь с такими данными уже существует.'}), 400
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Пожалуйста, введите почту и пароль.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        return jsonify({
            'message': 'Вход выполнен!',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'tag': user['tag'],
                'avatar': user['avatar'],
                'verified': user['verified'] if user['verified'] is not None else 0
            }
        }), 200
    else:
        return jsonify({'error': 'Неверная почта или пароль.'}), 401

@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    tag = data.get('tag')
    avatar = data.get('avatar')
    if not user_id or not name:
        return jsonify({'error': 'Имя обязательно для заполнения!'}), 400
    success, message = update_user_profile(user_id, name, tag, avatar)
    if success:
        updated_user = get_user_by_id(user_id)
        return jsonify({'message': message, 'user': updated_user}), 200
    else:
        return jsonify({'error': message}), 400