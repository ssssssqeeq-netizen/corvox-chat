import random
from flask import Blueprint, request, jsonify
from database import _call, is_email_taken, is_tag_taken, get_user_by_id
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
    send_verification_code(email, code)
    return jsonify({'message': 'Код отправлен'}), 200


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
    return jsonify({'error': 'Неверный код'}), 400


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    tag = data.get('tag')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'error': 'Заполните все поля'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Пароль минимум 8 символов'}), 400

    # Хэш передаём через API, но на Beget password_hash уже делает свою работу
    result, err = _call('register',
                        email=email, name=name,
                        tag=tag, password=password)
    if not result:
        return jsonify({'error': err}), 400
    return jsonify({'message': 'Регистрация успешна'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Введите почту и пароль'}), 400
    result, err = _call('login', email=email, password=password)
    if not result:
        return jsonify({'error': err}), 401
    return jsonify({'message': 'Вход выполнен', 'user': result.get('user')}), 200


@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    tag = data.get('tag')
    avatar = data.get('avatar')
    if not user_id or not name:
        return jsonify({'error': 'Имя обязательно'}), 400
    result, err = _call('update_profile',
                        user_id=user_id, name=name,
                        tag=tag, avatar=avatar)
    if not result:
        return jsonify({'error': err}), 400
    return jsonify({'message': 'Профиль обновлён', 'user': result.get('user')}), 200
