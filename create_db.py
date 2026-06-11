from app import create_app  # import hàm tạo app Flask
from extensions import db  # import database (SQLAlchemy)

app = create_app()  # khởi tạo ứng dụng Flask

with app.app_context():
    # mở context Flask để thao tác database ngoài request

    # XÓA TOÀN BỘ DỮ LIỆU
    db.drop_all()
    # xóa toàn bộ bảng trong database (xóa sạch dữ liệu + cấu trúc bảng)

    # TẠO LẠI DATABASE
    db.create_all()
    # tạo lại tất cả bảng theo model hiện tại

    print("Database recreated!")
    # thông báo hoàn tất reset database