from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename

from models import Transaction
from extensions import db
from datetime import datetime
import os

transaction = Blueprint('transaction', __name__)

# =========================
# DASHBOARD
# =========================
@transaction.route('/dashboard')
@login_required
def dashboard():

    if current_user.monthly_income <= 0:
        return redirect(url_for('transaction.set_income'))

    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'income'
    ).scalar() or 0

    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense'
    ).scalar() or 0

    budget_limit = current_user.budget_limit or 0

    balance = current_user.monthly_income + total_income - total_expense

    # ADMIN thấy tất cả, USER chỉ thấy của mình
    if current_user.role == "admin":
        transactions = Transaction.query.all()
    else:
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        budget_limit=budget_limit,
        monthly_income=current_user.monthly_income
    )


# =========================
# SET INCOME
# =========================
@transaction.route('/set-income', methods=['GET', 'POST'])
@login_required
def set_income():

    if request.method == 'POST':
        current_user.monthly_income = float(request.form['income'])
        current_user.budget_limit = float(request.form['budget'])

        db.session.commit()
        flash("Đã cập nhật!", "success")

        return redirect(url_for('transaction.dashboard'))

    return render_template("set_income.html")


# =========================
# ADD TRANSACTION
# =========================
@transaction.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():

    categories = [
        'Ăn uống', 'Mua sắm', 'Lương',
        'Thưởng', 'Giải trí', 'Chi phí nhà ở và đi lại'
    ]

    if request.method == 'POST':

        title = request.form.get('title')
        amount = request.form.get('amount')
        category = request.form.get('category')
        type_ = request.form.get('type')
        date = request.form.get('date')

        if not title or not amount or not category or not type_ or not date:
            flash("Vui lòng nhập đầy đủ thông tin!")
            return redirect(url_for('transaction.add_transaction'))

        try:
            amount = float(amount)
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except:
            flash("Dữ liệu không hợp lệ!")
            return redirect(url_for('transaction.add_transaction'))

        # CREATE TRANSACTION (FIX QUAN TRỌNG)
        new_transaction = Transaction(
            title=title,
            amount=amount,
            category=category,
            type=type_,
            date=date,
            user_id=current_user.id
        )

        db.session.add(new_transaction)
        db.session.commit()

        flash("Thêm giao dịch thành công!", "success")
        return redirect(url_for('transaction.dashboard'))

    return render_template("add_transaction.html", categories=categories)


# =========================
# EDIT TRANSACTION
# =========================
@transaction.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):

    transaction_data = Transaction.query.get_or_404(id)

    if current_user.role != "admin" and transaction_data.user_id != current_user.id:
        flash("Bạn không có quyền sửa!")
        return redirect(url_for('transaction.dashboard'))

    if request.method == 'POST':

        transaction_data.title = request.form['title']
        transaction_data.amount = float(request.form['amount'])
        transaction_data.category = request.form['category']
        transaction_data.type = request.form['type']
        transaction_data.date = datetime.strptime(request.form['date'], "%Y-%m-%d")

        db.session.commit()

        flash("Cập nhật thành công!")
        return redirect(url_for('transaction.dashboard'))

    return render_template("edit_transaction.html", transaction=transaction_data)


# =========================
# DELETE TRANSACTION
# =========================
@transaction.route('/delete/<int:id>')
@login_required
def delete_transaction(id):

    transaction_data = Transaction.query.get_or_404(id)

    if current_user.role != "admin" and transaction_data.user_id != current_user.id:
        flash("Bạn không có quyền xóa!")
        return redirect(url_for('transaction.dashboard'))

    db.session.delete(transaction_data)
    db.session.commit()

    flash("Xóa thành công!")
    return redirect(url_for('transaction.dashboard'))