from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import (login_user,logout_user,login_required,current_user)
from werkzeug.security import (generate_password_hash,check_password_hash)
from models import User, Transaction
from extensions import db

import os

# Blueprint
auth = Blueprint('auth', __name__)


# =========================
# LOGIN
# =========================

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            role = (user.role or "").strip().lower()

            if role == "admin":
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('transaction.dashboard'))

        flash("Sai tài khoản hoặc mật khẩu", "danger")

    return render_template('login.html')


# =========================
# REGISTER
# =========================

@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = (request.form.get('username') or "").strip()

        email = (request.form.get('email') or "").lower()

        password = request.form.get('password')

        confirm_password = request.form.get(
            'confirm_password'
        )

        # Kiểm tra password
        if password != confirm_password:

            flash("Mật khẩu không khớp")

            return redirect(
                url_for('auth.register')
            )

        # Kiểm tra username
        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash("Username đã tồn tại")

            return redirect(
                url_for('auth.register')
            )

        # Kiểm tra email
        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash("Email đã tồn tại")

            return redirect(
                url_for('auth.register')
            )

        # Mã hóa password
        hashed_password = generate_password_hash(
            password
        )

        # Tạo user
        new_user = User(

            username=username,

            email=email,

            password=hashed_password,

            role='user'
        )

        db.session.add(new_user)

        db.session.commit()

        flash("Đăng ký thành công")

        return redirect(url_for('auth.login'))

    return render_template('register.html')


# =========================
# CHANGE PASSWORD
# =========================

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():

    if request.method == 'POST':

        old_password = request.form.get('old_password')

        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            flash("Vui lòng nhập đầy đủ mật khẩu!", "danger")
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash("Mật khẩu mới không khớp!", "danger")
            return redirect(url_for('auth.change_password'))

        # Kiểm tra mật khẩu mới

        if new_password != confirm_password:

            flash("Mật khẩu mới không khớp!")

            return redirect(
                url_for('auth.change_password')
            )

        # Không cho trùng mật khẩu cũ

        if check_password_hash(
            current_user.password,
            new_password
        ):

            flash("Mật khẩu mới không được giống mật khẩu cũ!")

            return redirect(
                url_for('auth.change_password')
            )

        # Cập nhật

        current_user.password = generate_password_hash(
            new_password
        )

        db.session.commit()

        flash("Đổi mật khẩu thành công!", "success")

        return redirect(
            url_for('transaction.dashboard')
        )

    return render_template(
        'change_password.html'
    )



# =========================
# LOGOUT
# =========================

@auth.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('auth.login'))

# =========================
# DELETE ACCOUNT
# =========================

@auth.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():

    if request.method == 'POST':

        password = request.form.get('password')

        # Kiểm tra mật khẩu
        if not check_password_hash(
            current_user.password,
            password
        ):
            flash("Mật khẩu không chính xác!")
            return redirect(
                url_for('auth.delete_account')
            )

        # Xóa tất cả giao dịch
        Transaction.query.filter_by(
            user_id=current_user.id
        ).delete()

        user = User.query.get(current_user.id)

        logout_user()

        db.session.delete(user)
        db.session.commit()

        flash("Tài khoản đã được xóa.")

        return redirect(url_for('auth.login'))

    return render_template(
        'delete_account.html'
    )

