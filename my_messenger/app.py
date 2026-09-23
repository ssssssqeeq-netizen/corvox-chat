from flask import Flask, render_template
from database import init_db
from auth import auth_bp
from chat import chat_bp

app = Flask(__name__, template_folder='templates')

# Подключаем модули
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("Сервер запущен! Откройте http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)