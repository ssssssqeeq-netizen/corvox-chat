import requests

# ═══════════════════════════════════════════════════════════
# ПОДКЛЮЧЕНИЕ К API НА BEGET
# ═══════════════════════════════════════════════════════════
API_URL = "http://u95249rt.beget.tech/api.php"
SECRET_KEY = "corvox_super_secret_2026_xyz"


def _call(action, **params):
    """Универсальный вызов API."""
    params['action'] = action
    params['secret_key'] = SECRET_KEY
    try:
        r = requests.post(API_URL, json=params, timeout=15)
        data = r.json()
        if not data.get('ok'):
            return None, data.get('error', 'Неизвестная ошибка')
        return data, None
    except Exception as e:
        print(f"[API ERROR] {action}: {e}")
        return None, str(e)


def init_db():
    """Ничего не делаем — таблицы уже созданы на Beget."""
    print("Подключение к базе данных на Beget... OK")


# ═══════════════════════════════════════════════════════════
# ПОЛЬЗОВАТЕЛИ
# ═══════════════════════════════════════════════════════════
def is_email_taken(email):
    data, err = _call('check', email=email)
    if not data: return False
    return data.get('email_taken', False)


def is_tag_taken(tag):
    if not tag: return False
    data, err = _call('check', tag=tag)
    if not data: return False
    return data.get('tag_taken', False)


def search_users(query, current_user_id):
    data, err = _call('search', query=query, current_user_id=current_user_id)
    if not data: return []
    return data.get('users', [])


def update_user_profile(user_id, name, tag, avatar):
    data, err = _call('update_profile',
                      user_id=user_id, name=name,
                      tag=tag, avatar=avatar)
    if not data:
        return False, err or 'Ошибка'
    return True, "Профиль успешно обновлён!"


def get_user_by_id(user_id):
    # В этом API нет отдельного маршрута, но можно использовать login-ответ
    # А пока вернём заглушку
    return None


# ═══════════════════════════════════════════════════════════
# ЧАТЫ
# ═══════════════════════════════════════════════════════════
def get_or_create_chat(u1, u2):
    data, err = _call('create_chat', user1_id=u1, user2_id=u2)
    if not data: return None
    return data.get('chat_id')


def get_user_chats(user_id):
    data, err = _call('list_chats', user_id=user_id)
    if not data: return []
    return data.get('chats', [])


def save_message(chat_id, user_id, text):
    _call('send_message', chat_id=chat_id, user_id=user_id, text=text)


def save_voice_message(chat_id, user_id, audio_base64):
    _call('send_voice', chat_id=chat_id, user_id=user_id, audio=audio_base64)


def get_chat_messages(chat_id):
    data, err = _call('get_messages', chat_id=chat_id)
    if not data: return []
    return data.get('messages', [])


# ═══════════════════════════════════════════════════════════
# ГАЛОЧКА
# ═══════════════════════════════════════════════════════════
def toggle_verified_by_tag(tag):
    data, err = _call('toggle_verified', tag=tag)
    if not data: return None, None, None
    return data.get('name'), data.get('tag'), data.get('verified')
