import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATABASE = os.path.join(DATA_DIR, 'messenger.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            tag TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            avatar TEXT,
            verified INTEGER DEFAULT 0
        )
    ''')
    
    # На всякий случай добавляем колонку, если база старая
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN verified INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            is_group INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_members (
            chat_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (chat_id, user_id),
            FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных успешно инициализирована.")

# ============================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================

def is_email_taken(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def is_tag_taken(tag):
    if not tag: return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE tag = ?', (tag,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def update_user_profile(user_id, name, tag, avatar):
    conn = get_db_connection()
    cursor = conn.cursor()
    if tag:
        cursor.execute('SELECT id FROM users WHERE tag = ? AND id != ?', (tag, user_id))
        if cursor.fetchone():
            conn.close()
            return False, "Этот тег уже занят другим пользователем."
    if avatar:
        cursor.execute('UPDATE users SET name = ?, tag = ?, avatar = ? WHERE id = ?', (name, tag, avatar, user_id))
    else:
        cursor.execute('UPDATE users SET name = ?, tag = ? WHERE id = ?', (name, tag, user_id))
    conn.commit()
    conn.close()
    return True, "Профиль успешно обновлён!"

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, tag, avatar, verified FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def search_users(query, current_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, tag, avatar, verified FROM users 
        WHERE (name LIKE ? OR tag LIKE ?) AND id != ?
    ''', (f'%{query}%', f'%{query}%', current_user_id))
    users = cursor.fetchall()
    conn.close()
    return [dict(u) for u in users]

# ============================================================
# 🔵 ГАЛОЧКА ПОДТВЕРЖДЕНИЯ (для консольной админки)
# ============================================================

def toggle_verified_by_tag(tag):
    """Переключает галочку: была — убирает, не было — ставит."""
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_tag = tag.lstrip('@').strip()
    
    cursor.execute('SELECT id, name, verified FROM users WHERE tag = ?', (clean_tag,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return None, None, None  # Пользователь не найден
    
    new_value = 0 if user['verified'] == 1 else 1
    cursor.execute('UPDATE users SET verified = ? WHERE id = ?', (new_value, user['id']))
    conn.commit()
    conn.close()
    
    return user['name'], clean_tag, new_value

# ============================================================
# ЧАТЫ
# ============================================================

def get_or_create_chat(user1_id, user2_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.id FROM chats c
        JOIN chat_members m1 ON c.id = m1.chat_id
        JOIN chat_members m2 ON c.id = m2.chat_id
        WHERE c.is_group = 0 AND m1.user_id = ? AND m2.user_id = ?
    ''', (user1_id, user2_id))
    chat = cursor.fetchone()
    if chat:
        conn.close()
        return chat['id']
    cursor.execute('INSERT INTO chats (is_group) VALUES (0)')
    chat_id = cursor.lastrowid
    cursor.execute('INSERT INTO chat_members (chat_id, user_id) VALUES (?, ?)', (chat_id, user1_id))
    cursor.execute('INSERT INTO chat_members (chat_id, user_id) VALUES (?, ?)', (chat_id, user2_id))
    conn.commit()
    conn.close()
    return chat_id

def get_user_chats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.id as chat_id, u.name as peer_name, u.tag as peer_tag, u.avatar as peer_avatar, u.verified as peer_verified
        FROM chats c
        JOIN chat_members m1 ON c.id = m1.chat_id AND m1.user_id = ?
        JOIN chat_members m2 ON c.id = m2.chat_id AND m2.user_id != ?
        JOIN users u ON m2.user_id = u.id
        WHERE c.is_group = 0
    ''', (user_id, user_id))
    chats = cursor.fetchall()
    conn.close()
    return [dict(c) for c in chats]

def save_message(chat_id, user_id, text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (chat_id, user_id, text) VALUES (?, ?, ?)', (chat_id, user_id, text))
    conn.commit()
    conn.close()

def get_chat_messages(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.id, m.text, m.created_at, u.name as sender_name, u.avatar as sender_avatar, u.verified as sender_verified, m.user_id
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.chat_id = ?
        ORDER BY m.created_at ASC
    ''', (chat_id,))
    messages = cursor.fetchall()
    conn.close()
    return [dict(msg) for msg in messages]