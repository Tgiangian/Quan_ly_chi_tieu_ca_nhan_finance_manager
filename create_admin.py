from app import app  # import Flask app từ app.py
from extensions import db  # import database (SQLAlchemy)
from models import User  # import bảng User
from werkzeug.security import generate_password_hash  # dùng để mã hóa mật khẩu
import getpass  # nhập mật khẩu ẩn trong terminal

with app.app_context():
    # mở context Flask để thao tác database ngoài web

    print("DB URI =", app.config["SQLALCHEMY_DATABASE_URI"])  # in đường dẫn database
    print("INSTANCE PATH =", app.instance_path)  # in thư mục instance của Flask

    username = input("Username admin: ").strip()  
    # nhập username admin từ bàn phím

    # =========================
    # HẠ QUYỀN ADMIN CŨ
    # =========================
    admins = User.query.filter_by(role="admin").all()  
    # lấy tất cả user đang là admin

    for a in admins:
        print("Bỏ quyền admin:", a.username)  # thông báo user bị hạ quyền
        a.role = "user"  # đổi role admin → user

    # =========================
    # TÌM USER
    # =========================
    user = User.query.filter_by(username=username).first()  
    # tìm user theo username

    if user:
        # nếu user đã tồn tại

        print(f"Đã tìm thấy user: {user.username}")  # in username
        print(f"Role hiện tại: {user.role}")  # in role hiện tại

        password = getpass.getpass("Mật khẩu mới cho admin: ")  
        # nhập mật khẩu admin (ẩn ký tự)

        user.role = "admin"  # nâng quyền thành admin
        user.password = generate_password_hash(password)  # đổi mật khẩu (mã hóa)

        db.session.commit()  # lưu thay đổi vào database

        print("=== CẬP NHẬT THÀNH CÔNG ===")

    else:
        # nếu user chưa tồn tại → tạo mới admin

        email = input("Email admin: ").strip().lower()  
        # nhập email

        password = getpass.getpass("Password admin: ")  
        # nhập mật khẩu admin

        admin = User(
            username=username,  # username admin
            email=email,  # email admin
            password=generate_password_hash(password),  # mã hóa password
            role="admin"  # gán quyền admin
        )

        db.session.add(admin)  # thêm user mới vào database
        db.session.commit()  # lưu database

        print("=== TẠO ADMIN THÀNH CÔNG ===")

    # =========================
    # LIST ADMIN
    # =========================
    admins = User.query.filter_by(role="admin").all()  
    # lấy lại danh sách admin sau khi cập nhật

    for a in admins:
        print(a.username, "-", a.role)  
        # in danh sách admin