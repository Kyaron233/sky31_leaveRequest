from flask import Flask, request, session, jsonify,Blueprint
from ..database import get_connection
import mysql.connector
import logging
import pandas as pd
admin_bp = Blueprint('admin', __name__)
logging.basicConfig(level=logging.INFO)

@admin_bp.route('/login', methods=['POST'])
def login():
    admin_id = request.json.get('admin_id')
    password = request.json.get('password')

    if admin_id is None or password is None:
        return jsonify({"message": "输入错误"}), 401

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s AND pswd_hash = %s', (admin_id, password))
        user = cursor.fetchone()

        if user is not None:
            session['admin_id'] = user['admin_id']
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

@admin_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('admin_id', None)
    session.pop('name', None)
    return jsonify({"message": "账号已退出！"}), 200

@admin_bp.route('/query', methods=['GET'])
def query_user_by_department():
    if session.get('admin_id') is None:
        return jsonify({"message": "登录状态失效！"})
    department = request.args.get('department')

    if not department:
        return jsonify({"message": "部门名称参数缺失"}), 400

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM student WHERE department = %s', (department,))
        users = cursor.fetchall()

        if not users:
            return jsonify({"message": "未找到该部门的用户"}), 404

        result = [{"id": user["id"], "name": user["name"], "department": user["department"]} for user in users]
        return jsonify({"users": result}), 200

    except mysql.connector.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@admin_bp.route('/idquery', methods=['GET'])
def student_idquery():
    if session.get('admin_id') is None:
        return jsonify({"message": "登录状态失效！"})
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({"message": "学号参数缺失"}), 400

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM student WHERE student_id = %s', (student_id,))
        users = cursor.fetchall()
        if not users:
            return jsonify({"message": "未找到该用户"}), 404

        result = [{"id": user["id"], "name": user["name"], "department": user["department"]} for user in users]
        return jsonify({"users": result}), 200

    except mysql.connector.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@admin_bp.route('/add', methods=['POST'])
def add_user():
    student_id = request.json.get('student_id')
    name = request.json.get('name')
    department = request.json.get('department')
    role_in_depart = request.json.get('role_in_depart')
    tel = request.json.get('tel')
    password = request.json.get('password')

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('INSERT INTO student (student_id, name, tel, department, role_in_depart, password) VALUES (%s, %s, %s, %s, %s, %s)', (student_id, name, tel, department, role_in_depart, password))
        connection.commit()
        return jsonify({"message": "用户添加成功"}), 200
    except Exception as e:
        logging.error(f"发生错误: {str(e)}")
        return jsonify({"message": f"添加用户失败: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@admin_bp.route('/update', methods=['POST'])
def update_user():
    student_id = request.json.get('student_id')
    name = request.json.get('name')
    tel = request.json.get('tel')
    department = request.json.get('department')
    role_in_depart = request.json.get('role_in_depart')

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('UPDATE student SET name = %s, tel = %s, department = %s, role_in_depart = %s WHERE student_id = %s', (name, tel, department, role_in_depart, student_id))
        connection.commit()
        return jsonify({"message": "用户修改成功"}), 200
    except mysql.connector.Error as e:
        return jsonify({"message": f"修改失败：{str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@admin_bp.route('/delete', methods=['POST'])
def delete_user():
    student_id = request.json.get('student_id')

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('DELETE FROM student WHERE student_id = %s', (student_id,))
        connection.commit()
        return jsonify({"message": "用户删除成功"}), 200
    except mysql.connector.Error as e:
        return jsonify({"message": f"删除失败：{str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# excel表导入
@admin_bp.route('/import', methods=['POST'])
def import_users():
    if session.get('admin_id') is None:
        return jsonify({"message": "登录状态失效！"})

    if 'file' not in request.files:
        return jsonify({"message": "未找到文件"}), 400

    file = request.files['file']

    if not file.filename.endswith('.xlsx'):
        return jsonify({"message": "文件类型错误，只支持Excel文件"}), 400

    connection = None
    cursor = None
    try:
        # 读取所有工作表
        dfs = pd.read_excel(file, sheet_name=None)
        required_columns = {'student_id', 'name', 'department', 'role_in_depart', 'tel', 'password'}

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        for sheet_name, df in dfs.items():
            # 检查当前工作表是否包含必要的列
            if not required_columns.issubset(df.columns):
                return jsonify({"message": f"工作表 '{sheet_name}' 缺少必要的列"}), 400

            for _, row in df.iterrows():
                cursor.execute(
                    'INSERT INTO student (student_id, name, tel, department, role_in_depart, password) VALUES (%s, %s, %s, %s, %s, %s)',
                    (row['student_id'], row['name'], row['tel'], row['department'], row['role_in_depart'], row['password'])
                )

        connection.commit()
        return jsonify({"message": "用户导入成功"}), 200

    except Exception as e:
        logging.error(f"发生错误: {str(e)}")
        return jsonify({"message": f"导入用户失败: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
