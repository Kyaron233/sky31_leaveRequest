from app import user
from app.admin import admin
import secrets
from app.setup_db import setup_db


app = setup_db()
app.secret_key=secrets.token_urlsafe(64)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(user, url_prefix='/user')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)


