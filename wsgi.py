from app import app  
# import ứng dụng Flask đã được tạo sẵn từ file app.py

if __name__ == "__main__":  
    # kiểm tra xem file này có đang được chạy trực tiếp không
    # (không phải bị import từ file khác)

    app.run()  
    # chạy server Flask (mở web local)