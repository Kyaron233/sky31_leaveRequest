from flask import Flask
from app.admin import admin_bp
from app.user import user_bp
from app.config import Config
from app.database import get_connection

app = Flask(__name__)
app.config.from_object(Config)

# 注册管理员蓝图
app.register_blueprint(admin_bp, url_prefix='/admin')

# 注册用户蓝图
app.register_blueprint(user_bp, url_prefix='/user')