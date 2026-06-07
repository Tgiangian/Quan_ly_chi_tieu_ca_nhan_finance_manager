from flask import Flask, redirect, url_for
from extensions import db, login_manager


def create_app():

    app = Flask(__name__)

    # =========================
    # CONFIG
    # =========================
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    # =========================
    # INIT EXTENSIONS
    # =========================
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # =========================
    # IMPORT MODEL
    # =========================
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # =========================
    # BLUEPRINTS
    # =========================
    from routes.auth_routes import auth
    from routes.transaction_routes import transaction
    from routes.admin_routes import admin

    app.register_blueprint(auth)
    app.register_blueprint(transaction)
    app.register_blueprint(admin, url_prefix="/admin")

    # =========================
    # ROUTE HOME
    # =========================
    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    # =========================
    # CREATE DB
    # =========================
    with app.app_context():
        db.create_all()

    return app


# =========================
# RUN LOCAL ONLY
# =========================
app = create_app()

if __name__ == "__main__":
    app.run()