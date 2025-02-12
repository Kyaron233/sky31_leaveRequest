from flask import Flask, g
import mariadb


def setup_db():
    app = Flask(__name__)

    # 数据库配置
    app.config['DB_CONFIG'] = {
        'host': 'db',
        'port': 3306,
        'user': 'root',
        'password': '240700',
        'database': 'sky31Employees',
        'autocommit': True
    }

    # 请求前自动创建连接
    @app.before_request
    def before_request():
        try:
            g.conn = mariadb.connect(**app.config['DB_CONFIG'])
            g.cursor = g.conn.cursor(dictionary=True)
        except mariadb.Error as e:
            print(f"数据库错误 {e}")
            return "数据库错误", 500

    # 请求后自动关闭连接
    @app.teardown_request
    def teardown_request(exception=None):
        if hasattr(g, 'cursor'):
            g.cursor.close()
        if hasattr(g, 'conn'):
            g.conn.close()

    return app