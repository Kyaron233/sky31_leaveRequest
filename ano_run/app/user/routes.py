from flask import Blueprint,request,jsonify,session
from ..database import get_connection
import mysql.connector
import logging

user_bp = Blueprint('user', __name__)

logging.basicConfig(level=logging.INFO)

@user_bp.route('/login', methods=['POST'])
def login():
    user_id = request.json.get('user_id')
    password = request.json.get('password')

    if user_id is None or password is None:
        return jsonify({"message": "输入错误"}), 401

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM student WHERE student_id = %s AND password = %s', (user_id, password))
        user = cursor.fetchone()

        if user is not None:
            session['student_id'] = user['student_id']
            session['name'] = user['name']
            return jsonify({"message": "登陆成功"}), 200
        else:
            return jsonify({"message": "输入错误"}), 401

    except mysql.connector.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@user_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('student_id', None)
    session.pop('name', None)
    return jsonify({"message": "账号已退出！"}), 200

@user_bp.route('/info', methods=['GET'])
def info():
    # 检查用户是否登录
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

    user_id = session['student_id']
    connection = None
    cursor = None
    try:
        # 建立数据库连接
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        # 从数据库中查询用户信息
        query = "SELECT student_id, name, department, role_in_depart, tel FROM student WHERE student_id = %s"
        cursor.execute(query, (user_id,))
        user_info = cursor.fetchone()

        if user_info:
            return jsonify(user_info), 200
        else:
            return jsonify({"message": "未找到用户信息"}), 404

    except mysql.connector.Error as e:
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        # 关闭游标和数据库连接
        if cursor:
            cursor.close()
        if connection:
            connection.close()
