from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app # import các thư viện cần thiết
from flask_login import login_required, current_user # quản lý đăng nhập
from sqlalchemy import func # dùng các hàm tính toán SQL
from werkzeug.utils import secure_filename # xử lý tên file upload

from models import Transaction  # import bảng Transaction
from extensions import db # import database
from datetime import datetime # xử lý ngày tháng
import os # làm việc với hệ điều hành

#biến lưu blueprint(một module dùng để chia ứng dụng flask thành nhiều phần nhỏ )
# quản lý các chức năng xác thực
transaction = Blueprint('transaction', __name__)

# =========================
# DASHBOARD : bảng điều khiển
# =========================
@transaction.route('/dashboard') #tạo route dashboard 
@login_required # ycau đăng nhập
def dashboard():# định nghĩa hàm 

    if current_user.monthly_income <= 0: # kiểm tra đã thu nhập chưa
        return redirect(url_for('transaction.set_income')) #chưa thì chuyển sâng trang thiết lập 

    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,# lấy giao dịch của người dùng
        Transaction.type == 'income'#chỉ lấy giao dịch thu
    ).scalar() or 0 # tính tổng thu nhập

    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id, #lấy giao dịch của ng dùng
        Transaction.type == 'expense' # chỉ lấy giao dịch chi
    ).scalar() or 0 #tính tổng chi

    budget_limit = current_user.budget_limit or 0 #lấy hạn mức chi tiêu
    balance = current_user.monthly_income + total_income - total_expense #tính số dư

    # ADMIN thấy tất cả, USER chỉ thấy của mình
    if current_user.role == "admin": #ktra quyền adm
        transactions = Transaction.query.all() #adm xem tca giao dịch
    else:
        transactions = Transaction.query.filter_by(user_id=current_user.id).all() #user chỉ xem của mình

    return render_template(
        "dashboard.html", # hiện thị trên daashboard 
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        budget_limit=budget_limit,
        monthly_income=current_user.monthly_income
    )


# =========================
# SET INCOME : thiết lập thu thập và và hạn mức
# =========================
#get : lấy dữ liệu or hthi trang
#post : gửi dữ liệu lên server để xly or thay đổi

@transaction.route('/set-income', methods=['GET', 'POST']) # tạo route thiết lập thu thập
@login_required # ycau đnhap
def set_income():# định nghĩa hàm 

    if request.method == 'POST': #ktra gửi form
        current_user.monthly_income = float(request.form['income']) # cập nhật thu thập
        current_user.budget_limit = float(request.form['budget'])# cập nhật hạn mức

        db.session.commit()#lưu csdl
        flash("Đã cập nhật!", "success")# hthi tbao
        return redirect(url_for('transaction.dashboard'))# qlai về dashboard 

    return render_template("set_income.html")# hthi giao diện


# =========================
# ADD TRANSACTION : thêm giao dịch
# =========================
#get : lấy dữ liệu or hthi trang
#post : gửi dữ liệu lên server để xly or thay đổi 

@transaction.route('/add', methods=['GET', 'POST']) #tạo route thêm giao dịch
@login_required # ycau đnhap
def add_transaction():# định nghĩa hàm

    categories = [
        'Ăn uống', 'Mua sắm', 'Lương',
        'Thưởng', 'Giải trí', 'Chi phí nhà ở và đi lại'
    ]#danh sách mục giao dịch

    if request.method == 'POST': #ktra có gửi form ko

        title = request.form.get('title') #lấy tiêu đề
        amount = request.form.get('amount') # lấy số tiền
        category = request.form.get('category') #lấy danh mục
        type_ = request.form.get('type')# lấy loại gdich
        date = request.form.get('date') #lấy ngày gdich

        if not title or not amount or not category or not type_ or not date: #ktra dlieu
            flash("Vui lòng nhập đầy đủ thông tin!") #tbao lỗi
            return redirect(url_for('transaction.add_transaction')) # qlai trang thêm

        try:
            amount = float(amount) # chuyển số tiền sang số thực
            date = datetime.strptime(date, "%Y-%m-%d").date() # chuyển ngày tháng
        except:
            flash("Dữ liệu không hợp lệ!") #hthi tbao
            return redirect(url_for('transaction.add_transaction')) #qlai trang

        # CREATE TRANSACTION (FIX QUAN TRỌNG)
        new_transaction = Transaction( # tạo gdich mới
            title=title,
            amount=amount,
            category=category,
            type=type_,
            date=date,
            user_id=current_user.id # gắn giao dịch cho ng dùng htai
        )

        db.session.add(new_transaction) # thêm gdich
        db.session.commit() # lưu csdl

        flash("Thêm giao dịch thành công!", "success") #tbao thành công
        return redirect(url_for('transaction.dashboard')) # qlai trang

    return render_template("add_transaction.html", categories=categories) #hti giao diện thêm gdich


# =========================
# EDIT TRANSACTION : chỉnh sửa chức năng
# =========================
#get : lấy dữ liệu or hthi trang
#post : gửi dữ liệu lên server để xly or thay đổi 

@transaction.route('/edit/<int:id>', methods=['GET', 'POST']) # tạo route chỉnh sửa gdich
@login_required #ycau đăng nhập
def edit_transaction(id):#định nghĩa hàm thêm giao dịch

    transaction_data = Transaction.query.get_or_404(id) #tìm giao dịch theo id , không có thì báo lỗi 

    if current_user.role != "admin" and transaction_data.user_id != current_user.id:#ktra quyền sửa
        flash("Bạn không có quyền sửa!")#hthi tbao lỗi
        return redirect(url_for('transaction.dashboard')) #chuyển về dashboard

    if request.method == 'POST': #ktra ng dùng gửi form

        transaction_data.title = request.form['title'] # cập nhật tiêu đề
        transaction_data.amount = float(request.form['amount'])#cập nhật số tiền
        transaction_data.category = request.form['category']# cập nhật danh mục
        transaction_data.type = request.form['type']#cập nhạta loại gdich
        transaction_data.date = datetime.strptime(request.form['date'], "%Y-%m-%d") # cập nhật ngày tháng

        db.session.commit()#lưu thay dổi vào csdl

        flash("Cập nhật thành công!")# hthi thông báo
        return redirect(url_for('transaction.dashboard')) # qlai màn hình dashboard 

    return render_template("edit_transaction.html", transaction=transaction_data) #hiển thị giao diện chỉnh sửa


# =========================
# DELETE TRANSACTION ;xóa giao dịch
# =========================
@transaction.route('/delete/<int:id>') # tạo route xóa gdich
@login_required #ycau đnhap
def delete_transaction(id): # định ghĩa hàm xóa giao dịch

    transaction_data = Transaction.query.get_or_404(id) #tìm gdich theo id , ko có thì lỗi

    if current_user.role != "admin" and transaction_data.user_id != current_user.id: #ktra quyền xóa
        flash("Bạn không có quyền xóa!") #hthi tbao lỗi
        return redirect(url_for('transaction.dashboard')) # xóa gdich khỏi csdl

    db.session.delete(transaction_data) #xóa gdich khỏi csdl
    db.session.commit() # lưu csdl sau thay đổi

    flash("Xóa thành công!") # hthi tbao
    return redirect(url_for('transaction.dashboard')) #qlai trang dashboard 