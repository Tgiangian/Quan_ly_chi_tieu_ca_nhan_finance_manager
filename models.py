from extensions import db
from flask_login import UserMixin
from datetime import datetime, date


# =========================================
# USER MODEL
# =========================================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")
    monthly_income = db.Column(db.Float, default=0)
    budget_limit = db.Column(db.Float, default=0)
    # Đảm bảo đường dẫn này khớp với thực tế
    transactions = db.relationship("Transaction", backref="user", lazy=True)


# =========================================
# TRANSACTION MODEL
# =========================================

from datetime import date

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)