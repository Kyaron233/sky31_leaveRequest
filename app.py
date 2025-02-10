from flask import Flask, render_template, request ,blueprints
from admin.routes import admin
import secrets
from setup_db import setup_db


app = setup_db()
app.secret_key=secrets.token_urlsafe(64)
app.register_blueprint(admin, url_prefix='/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)


