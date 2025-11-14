from flask import Flask
from flask_cors import CORS
from models import db
from routes.organizations import org_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(app)  # чтобы фронтенд мог обращаться к серверу

# Регистрируем маршруты
app.register_blueprint(org_bp, url_prefix='/api/organizations')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

with app.app_context():
    db.create_all()  # создаёт таблицы, если их нет

if __name__ == '__main__':
    app.run(debug=True)
