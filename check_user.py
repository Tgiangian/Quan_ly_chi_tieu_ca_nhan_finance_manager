from app import app  # import app Flask từ file app.py
from models import User  # import bảng User từ database

with app.app_context():  
    # tạo context của Flask để có thể truy cập database bên ngoài request

    for u in User.query.all():  
        # lấy toàn bộ user trong database

        print(u.username, u.role)  
        # in ra username và role (admin/user) của từng người