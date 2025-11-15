from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.models import db
from backend.routes.organizations import org_bp
from backend.routes.auth import auth_bp
from backend.routes.admin import admin_bp
from backend.config import Config
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    # frontend dir one level up
    frontend_dir = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(org_bp, url_prefix='/api/organizations')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    with app.app_context():
        # ensure database file and tables exist
        db.create_all()

    # serve index.html at root
    @app.route('/')
    def index():
        return send_from_directory(frontend_dir, 'index.html')

    # serve admin page (if file exists)
    @app.route('/admin.html')
    def admin_page():
        return send_from_directory(frontend_dir, 'admin.html')

    return app

app = create_app()

if __name__ == '__main__':
    # When run directly:
    app.run(debug=True, host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))
