# liên kết :lấy các hàm , lớp hoặc đối tượng đã được định nghĩa trong thư viện hoặc các trang 
#chức năng : sử dụng mã nguồn đã được định nghĩa thay vì phải viết lại
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User
from extensions import db

#biến lưu blueprint(một module dùng để chia ứng dụng flask thành nhiều phần nhỏ )
admin = Blueprint("admin", __name__)

# =========================
# COUNT ADMIN : đếm admin
# =========================
# định nghĩa hàm count admin
# chức năng đếm số lượng tài khoản có quyền admin
def count_admins():
    #truy vấn bảng user trong cơ sở dữ liệu , lọc bản ghi có role = admin , đếm số lượng bản ghi đó bằng count() , trả về kqua cho def
    return User.query.filter_by(role="admin").count()


# =========================
# DASHBOARD : bảng điều khiển (trang tổng quan)
# =========================
@admin.route("/dashboard")#định nghĩa route cho blueprint admin 
@login_required #ycau phải đăng nhập được mới truy cập đc vào ( nếu chưa đnhap sẽ chuyển sang trang đnhap)
def dashboard():# định nghĩa hàm dashboard 

    if current_user.role != "admin": #ktra ngdung đang đnhap ,ko phải admin ko đc phép truy cập
        flash("Bạn không có quyền truy cập admin", "danger") #hiển thị lỗi thông báo cho người dùng . danger thuộc bootstrap( 1 công cụ gồm jvs và css để tke giao diện web)
        return redirect(url_for("transaction.dashboard")) #chuyển ng dùng về trang dashboard của phàn transaction và kêt thúc

    users = User.query.all() #lấy danh sách user trong csdl
    total_users = User.query.count() # đếm tổng số ng dùng
    total_transactions = sum(len(u.transactions) for u in users) #tính tổng số gdich của tát cả ng dùng = duyệt từng user và cộng sluong gdich 

    return render_template( #trả về giao diện html cho trình duyệt
        "admin_dashboard.html", #file gdien hiển thị
        users=users, #truyền danh sách user sang gdien
        total_users=total_users,# truyền tổng số user 
        total_transactions=total_transactions # chuyển tổng số gdich
    )


# =========================
# MAKE ADMIN : chức năng admin ( 3 admin)
# =========================
@admin.route("/make-admin/<int:user_id>", methods=["POST"]) #Tạo route admin, nhận user_id và chỉ nhận yêu cầu POST(gửi dl, tạo hoạc thay đổi dlieu) để cập nhật dữ liệu.
@login_required #ycau đăng nhập để sdung chức nang  để cập nhật dữ liệu.
def make_admin(user_id):#định nghĩa hàm ,nhận tham số user_id là id của ng muốn nâng lên admin

    if current_user.role != "admin":  #ktra ngdung đang đnhap ,ko phải admin ko đc phép truy cập
        return redirect(url_for("transaction.dashboard")) #chuyển ng dùng về trang dashboard của phàn transaction và kêt thúc

    user = User.query.get_or_404(user_id) # tìm ng dùng có id tương ứng trong csdl , nếu ko có thì trả flask về lỗi 404

    if user.role == "admin":#kiểm tra ng dùng là admin 
        flash("User đã là admin", "warning") # hiện thị tbao cảnh báo khi là admin
        return redirect(url_for("admin.dashboard")) #qlai trang dashboard 

    if count_admins() >= 3: # gọi hàm để đếm số adm htai . đủ 3 thì ko cấp quyền
        flash("Chỉ tối đa 3 admin", "danger") #hiển thị lỗi thông báo lỗi khi nếu cấp quyền cho ng4 trở lên
        return redirect(url_for("admin.dashboard")) #qlai trang quản trị

    user.role = "admin" #nếu dkien hợp lý thì thay đổi quyền thành adm
    db.session.commit() #lưu thay đổi thành csdl

    flash("Đã nâng user thành admin", "success") #hiển thị thành công thông báo cấp quyền thành công
    return redirect(url_for("admin.dashboard")) #hoàn thành, chuyển về trang dashboard của adm


# =========================
# TRANSFER ADMIN : nhượng quyền adm
# =========================
@admin.route("/transfer/<int:user_id>", methods=["POST"]) ##Tạo route admin, nhận user_id và chỉ nhận yêu cầu POST(gửi dl, tạo hoạc thay đổi dlieu) để cập nhật dữ liệu.
@login_required #ycau đnhap để thực hiện chức năng
def transfer_admin(user_id): #gọi hàm , nhận tham số user là id ng sẽ đc cấp quyền

    if current_user.role != "admin": #ktra ngdung đang đnhap ,ko phải admin ko đc phép truy cập
        return redirect(url_for("transaction.dashboard")) #chuyển ng dùng về trang dashboard của phàn transaction và kêt thúc

    new_admin = User.query.get_or_404(user_id)

    if new_admin.id == current_user.id:
        flash("Không thể tự nhượng quyền", "danger") #hiển thị lỗi thông báo cho người dùng . danger thuộc bootstrap( 1 công cụ gồm jvs và css để tke giao diện web)
        return redirect(url_for("admin.dashboard")) #chuyển ng dùng về trang dashboard của phàn admin và kêt thúc

    current_admin = current_user #gán user đang đnhap(adm htai) vào biến currentadm để dễ xly

    # đổi role
    current_admin.role = "user" #thay đổi quyền admin htai thành user 
    new_admin.role = "admin" #cấp quyền cho admin mới

    db.session.commit() #lưu các thay đổi xuống csdl

    flash("Đã nhượng quyền admin", "success") #hiển thị thông báo cấp quyền thành công bootstrap( 1 công cụ gồm jvs và css để tke giao diện web)

    return redirect(url_for("admin.dashboard")) #chuyển ng dùng về trang dashboard của phàn admin và kêt thúc


# =========================
# DELETE USER : xóa ng dùng
# =========================
@admin.route("/delete-user/<int:user_id>", methods=["POST"]) #Tạo route admin, nhận user_id và chỉ nhận yêu cầu POST(gửi dl, tạo hoạc thay đổi dlieu)
@login_required #ycau đăng nhập mới thực hiện đc chức năng
def delete_user(user_id):  #gọi hàm xóa ng dùng , nhận id user 

    if current_user.role != "admin": #ktra ngdung đang đnhap ,ko phải admin ko đc phép truy cập
        return redirect(url_for("transaction.dashboard")) #chuyển ng dùng về trang dashboard của phàn transaction 

    user = User.query.get_or_404(user_id) #tìm ng dùng theo user , ko có thì lỗi 404

    if user.id == current_user.id: #ktra adm có đang tự xóa mình ko
        flash("Không thể xóa chính mình", "danger") #hiển thị lỗi thông báo cho người dùng . danger thuộc bootstrap( 1 công cụ gồm jvs và css để tke giao diện web)
        return redirect(url_for("admin.dashboard")) #chuyển ng dùng về trang dashboard của admin 

    db.session.delete(user) #xóa ng dùng khỏi csdl
    db.session.commit() #lưu cập nhật csdl

    flash("Đã xóa user", "success") #hiển thị thành công thông báo cho người dùng . danger thuộc bootstrap( 1 công cụ gồm jvs và css để tke giao diện web)
    return redirect(url_for("admin.dashboard")) #chuyển ng dùng về trang dashboard của phàn admin và kêt thúc