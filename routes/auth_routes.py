# liên kết :lấy các hàm , lớp hoặc đối tượng đã được định nghĩa trong thư viện hoặc các trang 
#chức năng : sử dụng mã nguồn đã được định nghĩa thay vì phải viết lại
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import (login_user,logout_user,login_required,current_user)
from werkzeug.security import (generate_password_hash,check_password_hash)
from models import User, Transaction
from extensions import db

import os #lket thư viện

#biến lưu blueprint(một module dùng để chia ứng dụng flask thành nhiều phần nhỏ )
# quản lý các chức năng xác thực
auth = Blueprint('auth', __name__) 


# =========================
# LOGIN : đăng nhập 
# =========================
#get : lấy dữ liệu or hthi trang
#post : gửi dữ liệu lên server để xly or thay đổi

@auth.route('/login', methods=['GET', 'POST']) #tạo route đăng nhập , nhận get và post
def login(): #định nghĩa hàm đnhap 

    if request.method == 'POST': #ktra user có form đnhap ko

        username = request.form.get('username')#lấy user từ form
        password = request.form.get('password')#lấy password từ form

        user = User.query.filter_by(username=username).first() #tìm ng dùng theo user ,lấy bản ghi đầu tiên

        if user and check_password_hash(user.password, password): #ktra tài khoản tồn tại và mkhau đúng
            login_user(user) #đnhap user 
            role = (user.role or "").strip().lower() #lấy user ng dùng, bỏ khoảng trắng, chuyển về chữ thường
            if role == "admin":#ktra adm
                return redirect(url_for('admin.dashboard')) #quay vè dashboard  của adim
            else:#ktra user
                return redirect(url_for('transaction.dashboard')) # quay về dashboard của user 

        flash("Sai tài khoản hoặc mật khẩu", "danger") #hthi thông báo dnhap thất bại

    return render_template('login.html') # hthi giao diện đang nhập 


# =========================
# REGISTER : đang ký
# =========================
#get : lấy dữ liệu or hthi trang
#post : gửi dữ liệu lên server để xly or thay đổi

@auth.route('/register', methods=['GET', 'POST']) #tạo route đăng nhập , nhận get và post
def register():# định nghĩa hàm register

    if request.method == 'POST': #ktra user có gửi form đky ko
        username = (request.form.get('username') or "").strip() #lấy user và xóa khoảng tráng thừa
        email = (request.form.get('email') or "").lower() #lấy email và chuyển thành chữ thường
        password = request.form.get('password') #lấy mật khẩu
        confirm_password = request.form.get('confirm_password') #lấy mkhau xác nhận

        # Kiểm tra password
        if password != confirm_password: #ktra 2 mkhau giống nhau ko
            flash("Mật khẩu không khớp")#hthi thbao lỗi mkhau ko khớp
            return redirect(url_for('auth.register')) #quay về trang dky

        # Kiểm tra username
        existing_user = User.query.filter_by(username=username).first() #ktra email đã tồn tại chưa

        if existing_user: # ktra user đã tồn tại trong csdl chưa
            flash("Username đã tồn tại") #hthi tbao 
            return redirect(url_for('auth.register'))#qlai trang đăng ký

        # Kiểm tra email
        existing_email = User.query.filter_by(email=email).first() #tìm tkhoan có email vừa nhập trong csdl và lấy bản ghi đầu tiên

        if existing_email: #ktra email tồn tại trong csdl chưa

            flash("Email đã tồn tại") #hthi tbao
            return redirect(url_for('auth.register'))# quay về trang đăng ký

        # Mã hóa password
        hashed_password = generate_password_hash(password)#mã hóa mkhau ng dùng trc khi lưu vào csdl tăng bảo mật

        # Tạo user
        new_user = User(# tạo 1 đối tượng user mới 
            username=username, #gán user cho tkhoan
            email=email,#gán email cho tkhoan
            password=hashed_password,# gán lưu mật khẩu đã đc mã hóa 
            role='user' #gán quyền mắc định là user 
        )

        db.session.add(new_user)#thêm tkhoan mới vào vùng chờ của csdl
        db.session.commit() # lưu chính thức tài khoản mới vào csdl

        flash("Đăng ký thành công")# hthi tbao
        return redirect(url_for('auth.login'))# quay lại trang đăng nhập

    return render_template('register.html')# hthi giao diện đang ký khi ng dùng truy cập or khi chưa gửi form 


# =========================
# CHANGE PASSWORD
# =========================
#get : lấy dữ liệu or hthi trang
#post : gửi dữ liệu lên server để xly or thay đổi

@auth.route('/change-password', methods=['GET', 'POST'])#tạo route đăng nhập , nhận get và post
@login_required #ycau đnhap mới thực hiện chức năng
def change_password():# định nghĩa hàm đổi mật khẩu

    if request.method == 'POST':#ktra ng dùng có gửi form ko

        old_password = request.form.get('old_password')#lấy mmkhau cũ
        new_password = request.form.get('new_password')#lấy mật khẩu mới
        confirm_password = request.form.get('confirm_password')#lấy mật khẩu xác nhận

        if not new_password or not confirm_password:#ktra đã nhập đủ thông tin chưa
            flash("Vui lòng nhập đầy đủ mật khẩu!", "danger")#tbao lỗi 
            return redirect(url_for('auth.change_password'))#qlai trang đổi mkhau

        #ktra mkhau mới
        if new_password != confirm_password:#ktra 2 mkhau mới có khớp nhau ko
            flash("Mật khẩu mới không khớp!", "danger")#tbao lỗi
            return redirect(url_for('auth.change_password'))#qlai trang đổi mkhau

        # Không cho trùng mật khẩu cũ

        if check_password_hash(current_user.password,new_password):# ktra mkhau mới có giống mkhau cũ ko

            flash("Mật khẩu mới không được giống mật khẩu cũ!")#hthi thông báo 
            return redirect(url_for('auth.change_password'))#qlai trang đổi mkhau

        # Cập nhật
        current_user.password = generate_password_hash(new_password)#mã hóa và cập nhật mkhau

        db.session.commit()#lưu thay đổi vào csdl

        flash("Đổi mật khẩu thành công!", "success")# hthi tbao đổi mkhau thành công
        return redirect(url_for('transaction.dashboard'))#qlai trang dashboard 

    return render_template('change_password.html') #hthi giao diện đổi mkhau

# =========================
# LOGOUT : đăng xuất
# =========================

@auth.route('/logout') #tạo route đăng xuất 
@login_required #đăng nhập để thực hiện chức năng
def logout():#định nghĩa hàm đang xuất
    logout_user()#đăng xuât user , xóa phiên đăng nhập 
    return redirect(url_for('auth.login'))# chuyển về trang đăng nhập

# =========================
# DELETE ACCOUNT : cóa tài khoản 
# =========================
#get : lấy dữ liệu or hthi trang
#post : gửi dữ liệu lên server để xly or thay đổi

@auth.route('/delete-account', methods=['GET', 'POST']) #tạo route xóa tài khoản
@login_required #đăng nhập để thực hiên chức năng
def delete_account():#định nghĩa hàm xóa tài khoản

    if request.method == 'POST':# ktra ng dùng có gửi form ko
        password = request.form.get('password')#lấy mật khẩu xác nhận

        # Kiểm tra mật khẩu
        if not check_password_hash(current_user.password,password):#ktra mkhau nhập vào có đúng ko
            flash("Mật khẩu không chính xác!") #hthi thông báo 
            return redirect(url_for('auth.delete_account')) #quay về trang xóa tài khoản
        
        # Xóa tất cả giao dịch
        Transaction.query.filter_by(user_id=current_user.id).delete() #xóa toàn bộ giao dịch của tài khoản
        user = User.query.get(current_user.id) #lấy thông tin tkhoan htai
        logout_user()#đăng xuất tkhoan

        db.session.delete(user)#xóa tài khoản khỏi csdl
        db.session.commit()#lưu thay đổi vào csdl

        flash("Tài khoản đã được xóa.") #hiển thị tbao
        return redirect(url_for('auth.login')) #qlai trang đăng nhập

    return render_template('delete_account.html') #hthi giao diện xoá tài khoản

