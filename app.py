from admin import admin
import secrets
from flask import Flask
from setup_db import setup_db

app = Flask(__name__)
app = setup_db()
app.secret_key=secrets.token_urlsafe(64)
app.register_blueprint(admin, url_prefix='/admin')

@app.route('/')
def hello():
    return "hello!"