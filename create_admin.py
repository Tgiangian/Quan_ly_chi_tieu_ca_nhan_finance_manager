from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
import getpass

with app.app_context():

    print("DB URI =", app.config["SQLALCHEMY_DATABASE_URI"])
    print("INSTANCE PATH =", app.instance_path)

    username = input("Username admin: ").strip()

    # =========================
    # HẠ QUYỀN ADMIN CŨ
    # =========================
    admins = User.query.filter_by(role="admin").all()

    for a in admins:
        print("Bỏ quyền admin:", a.username)
        a.role = "user"

    # =========================
    # TÌM USER
    # =========================
    user = User.query.filter_by(username=username).first()

    if user:

        print(f"Đã tìm thấy user: {user.username}")
        print(f"Role hiện tại: {user.role}")

        password = getpass.getpass("Mật khẩu mới cho admin: ")

        user.role = "admin"
        user.password = generate_password_hash(password)

        db.session.commit()

        print("=== CẬP NHẬT THÀNH CÔNG ===")

    else:

        email = input("Email admin: ").strip().lower()
        password = getpass.getpass("Password admin: ")

        admin = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("=== TẠO ADMIN THÀNH CÔNG ===")

    # =========================
    # LIST ADMIN
    # =========================
    admins = User.query.filter_by(role="admin").all()

    for a in admins:
        print(a.username, "-", a.role)