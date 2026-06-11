from flask_sqlalchemy import SQLAlchemy  # thư viện ORM để làm việc với database trong Flask
from flask_login import LoginManager  # thư viện quản lý đăng nhập (session user)

# Database
db = SQLAlchemy()  
# tạo đối tượng database, chưa gắn app (sẽ gắn trong create_app)

# Login manager
login_manager = LoginManager()  
# tạo đối tượng quản lý đăng nhập, chưa gắn app (cũng sẽ gắn trong create_app)