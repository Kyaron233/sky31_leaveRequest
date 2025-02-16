from admin import admin
import secrets
from flask import Flask, make_response,session
from setup_db import setup_db
from flask_cors import CORS
from datetime import timedelta
from user import user_bp
import redis

app = Flask(__name__)
app = setup_db()
#CORS(app, supports_credentials=True)

app.secret_key = secrets.token_urlsafe(64)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user') # 未完成



#@app.after_request
#def after_request(response):
    #response.headers['Access-Control-Allow-Origin'] = '*' # 允许所有地址访问，测试用
    #response.headers['Access-Control-Allow-Credentials'] = 'true'
    #return response



@app.route('/')
def hello():
    return "hello!"


# 本地开发时，这里才会生效。生产环境使用 gunicorn 启动
if __name__ == '__main__':
    app.run(debug=True)

