from extensions import db  # import database SQLAlchemy đã khởi tạo từ extensions
from flask_login import UserMixin  # giúp Flask-Login hiểu User (login/logout/session)
from datetime import datetime, date  # dùng để xử lý ngày tháng


# =========================================
# USER MODEL (bảng user trong database)
# =========================================

class User(db.Model, UserMixin):
    # kế thừa db.Model → biến class thành bảng database
    # UserMixin → hỗ trợ login (is_authenticated, get_id,...)

    id = db.Column(db.Integer, primary_key=True)  
    # khóa chính (id user)
    username = db.Column(db.String(100), unique=True, nullable=False)  
    # tên đăng nhập (không trùng, không được để trống)
    email = db.Column(db.String(200), unique=True, nullable=False)  
    # email (không trùng, không được để trống)
    password = db.Column(db.String(200), nullable=False)  
    # mật khẩu đã mã hóa
    role = db.Column(db.String(20), default="user")  
    # quyền user: user / admin
    monthly_income = db.Column(db.Float, default=0)  
    # thu nhập tháng
    budget_limit = db.Column(db.Float, default=0)  
    # hạn mức chi tiêu
    transactions = db.relationship("Transaction", backref="user", lazy=True)  
    # liên kết 1-n:
    # 1 user có nhiều transaction
    # backref="user" → từ transaction gọi được .user


# =========================================
# TRANSACTION MODEL (bảng giao dịch)
# =========================================

class Transaction(db.Model):
    # tạo bảng Transaction trong database

    id = db.Column(db.Integer, primary_key=True)  
    # id giao dịch
    title = db.Column(db.String(200), nullable=False)  
    # tên giao dịch (ví dụ: ăn uống, lương,...)
    amount = db.Column(db.Float, nullable=False)  
    # số tiền
    category = db.Column(db.String(100), nullable=False)  
    # danh mục (ăn uống, mua sắm,...)
    type = db.Column(db.String(20), nullable=False)  
    # loại giao dịch: income / expense
    description = db.Column(db.Text)  
    # mô tả thêm (không bắt buộc)
    date = db.Column(db.Date, default=date.today)  
    # ngày giao dịch, mặc định là hôm nay
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    # khóa ngoại:
    # liên kết với bảng user (mỗi transaction thuộc 1 user)