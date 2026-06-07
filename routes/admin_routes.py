from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User
from extensions import db

admin = Blueprint("admin", __name__)

# =========================
# COUNT ADMIN
# =========================
def count_admins():
    return User.query.filter_by(role="admin").count()


# =========================
# DASHBOARD
# =========================
@admin.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        flash("Bạn không có quyền truy cập admin", "danger")
        return redirect(url_for("transaction.dashboard"))

    users = User.query.all()

    total_users = User.query.count()
    total_transactions = sum(len(u.transactions) for u in users)

    return render_template(
        "admin_dashboard.html",
        users=users,
        total_users=total_users,
        total_transactions=total_transactions
    )


# =========================
# MAKE ADMIN (MAX 3)
# =========================
@admin.route("/make-admin/<int:user_id>", methods=["POST"])
@login_required
def make_admin(user_id):

    if current_user.role != "admin":
        return redirect(url_for("transaction.dashboard"))

    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("User đã là admin", "warning")
        return redirect(url_for("admin.dashboard"))

    if count_admins() >= 3:
        flash("Chỉ tối đa 3 admin", "danger")
        return redirect(url_for("admin.dashboard"))

    user.role = "admin"
    db.session.commit()

    flash("Đã nâng user thành admin", "success")
    return redirect(url_for("admin.dashboard"))


# =========================
# TRANSFER ADMIN
# =========================
@admin.route("/transfer/<int:user_id>", methods=["POST"])
@login_required
def transfer_admin(user_id):

    if current_user.role != "admin":
        return redirect(url_for("transaction.dashboard"))

    new_admin = User.query.get_or_404(user_id)

    if new_admin.id == current_user.id:
        flash("Không thể tự nhượng quyền", "danger")
        return redirect(url_for("admin.dashboard"))

    current_admin = current_user

    # đổi role
    current_admin.role = "user"
    new_admin.role = "admin"

    db.session.commit()

    flash("Đã nhượng quyền admin", "success")

    return redirect(url_for("admin.dashboard"))


# =========================
# DELETE USER
# =========================
@admin.route("/delete-user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):

    if current_user.role != "admin":
        return redirect(url_for("transaction.dashboard"))

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("Không thể xóa chính mình", "danger")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(user)
    db.session.commit()

    flash("Đã xóa user", "success")
    return redirect(url_for("admin.dashboard"))