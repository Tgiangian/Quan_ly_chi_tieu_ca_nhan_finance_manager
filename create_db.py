from app import create_app
from extensions import db

app = create_app()

with app.app_context():

    # Xóa toàn bộ dữ liệu 
    db.drop_all()

    # Tạo lại bảng 
    db.create_all()

    print("Database recreated!")