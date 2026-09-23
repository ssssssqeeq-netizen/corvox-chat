from flask import Blueprint, request, jsonify
from database import search_users, get_or_create_chat, get_user_chats, save_message, get_chat_messages

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    current_user_id = data.get('current_user_id')
    
    if not query or not current_user_id:
        return jsonify({'error': 'Введите запрос для поиска'}), 400
        
    users = search_users(query, current_user_id)
    return jsonify({'users': users}), 200

@chat_bp.route('/create', methods=['POST'])
def create_chat():
    data = request.json
    user1_id = data.get('user1_id')
    user2_id = data.get('user2_id')
    
    if not user1_id or not user2_id:
        return jsonify({'error': 'Ошибка: не переданы ID пользователей'}), 400
        
    chat_id = get_or_create_chat(user1_id, user2_id)
    return jsonify({'chat_id': chat_id, 'message': 'Чат создан или найден'}), 200

@chat_bp.route('/list', methods=['POST'])
def list_chats():
    data = request.json
    user_id = data.get('user_id')
    
    chats = get_user_chats(user_id)
    return jsonify({'chats': chats}), 200

@chat_bp.route('/send', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    user_id = data.get('user_id')
    text = data.get('text')
    
    if not chat_id or not user_id or not text:
        return jsonify({'error': 'Все поля обязательны!'}), 400
        
    save_message(chat_id, user_id, text)
    return jsonify({'message': 'Отправлено'}), 200

@chat_bp.route('/messages/<int:chat_id>', methods=['GET'])
def chat_messages(chat_id):
    messages = get_chat_messages(chat_id)
    return jsonify({'messages': messages}), 200