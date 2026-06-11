from flask import Flask, redirect, url_for
from extensions import db, login_manager


def create_app():  # tạo app Flask theo kiểu factory (chuẩn dự án lớn)

    app = Flask(__name__)  # khởi tạo ứng dụng Flask

    # =========================
    # CONFIG (cấu hình app)
    # =========================
    app.config['SECRET_KEY'] = 'secretkey'  # khóa bảo mật session/login
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'  # kết nối database SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # tắt tracking để nhẹ hơn
    app.config['UPLOAD_FOLDER'] = 'static/uploads'  # thư mục lưu file upload

    # =========================
    # INIT EXTENSIONS (khởi tạo thư viện)
    # =========================
    db.init_app(app)  # gắn database vào app
    login_manager.init_app(app)  # gắn hệ thống login vào app
    login_manager.login_view = "auth.login"  # nếu chưa login → chuyển tới trang login

    # =========================
    # IMPORT MODEL USER
    # =========================
    from models import User  # import bảng User từ database

    @login_manager.user_loader
    def load_user(user_id):
        # hàm lấy user từ session khi người dùng đã đăng nhập
        return db.session.get(User, int(user_id))

    # =========================
    # IMPORT BLUEPRINT (chia module)
    # =========================
    from routes.auth_routes import auth  # module đăng nhập/đăng ký
    from routes.transaction_routes import transaction  # module giao dịch
    from routes.admin_routes import admin  # module admin

    # đăng ký các blueprint vào app
    app.register_blueprint(auth)
    app.register_blueprint(transaction)
    app.register_blueprint(admin, url_prefix="/admin")  # admin có prefix /admin

    # =========================
    # ROUTE HOME
    # =========================
    @app.route('/')
    def home():
        # khi vào "/" → chuyển thẳng tới trang login
        return redirect(url_for('auth.login'))

    # =========================
    # CREATE DATABASE
    # =========================
    with app.app_context():
        # tạo toàn bộ bảng trong database nếu chưa tồn tại
        db.create_all()

    return app  # trả về app đã cấu hình hoàn chỉnh


# =========================
# RUN APP (chạy local)
# =========================
app = create_app()  # tạo app

if __name__ == "__main__":
    app.run()  # chạy server Flask