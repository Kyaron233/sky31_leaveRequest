from flask import Flask, render_template, request ,blueprints
from admin.routes import admin
import secrets
app = Flask(__name__)
app.secret_key=secrets.token_urlsafe(64)
app.register_blueprint(admin, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)