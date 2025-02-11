from admin import admin
import secrets
from flask import Flask
from setup_db import setup_db

app = Flask(__name__)
app = setup_db()
app.secret_key=secrets.token_urlsafe(64)
app.register_blueprint(admin, url_prefix='/admin')

# 在服务器部署的代码中使用gunicorn，故删除了这里的启动（不过有点不方便本地调试）
@app.route('/')
def hello():
    return "hello!"