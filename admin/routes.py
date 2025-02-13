from flask import Blueprint, request, session,jsonify,make_response
from packages import hash_pswd,isPswdCorrect
from flask import g
import mariadb
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import secrets
import pandas as pd


# 蓝图
admin = Blueprint('admin', __name__)

#管理员需要的接口：登录，查询，增加，删除，退出登录，
#查询应该还要细分一下：按部门查询

ALLOWED_EXTENSIONS = {'xlsx,xls'} # 上传excel表格
MAX_FILE_SIZE = 1024*1024 * 10 # 10MB表格最大
MAX_CONTENT_LENGTH = MAX_FILE_SIZE


@admin.route('/login', methods=['POST'])
#登录
def login():
    admin_id=request.json.get('admin_id')
    password=request.json.get('password')


    try:
        g.cursor.execute('select * from admin where admin_id = %s', (admin_id,))
        user=g.cursor.fetchone()

        if user is not None:
            if isPswdCorrect(password,user['pswd_hash']):
                session['admin_id'] = user['admin_id']
                session['name'] = user['name']
                session.permanent = True  # 设置会话为永久有效

                session['session_id']=secrets.token_urlsafe(64)
                response = make_response(jsonify({"message":"登录成功！"}),200)
                response.set_cookie('session_id', session['session_id'], max_age=604800, secure=False)#secure应在正式环境改成true
                return response
            else:
                return jsonify({"message": "用户名与密码不匹配！"}), 401
        else :
            return jsonify({"message": "找不到用户！"}), 401

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500


@admin.route('/logout', methods=['POST'])
def logout():
    # 清除 session 中存储的登录信息
    session.pop('admin_id', None)
    session.pop('name', None)

    # 创建响应对象并设置状态码为 200（成功）
    response = make_response(jsonify({"message": "退出成功！"}), 200)

    # 清除 cookie 中的 session_id
    response.delete_cookie('session_id')

    session.permanent = False

    # 返回响应
    return response

@admin.route('/query',methods=['GET'])
def query_user_by_department():
    if not session.get('session_id'):  # 更严格的校验
        return jsonify({"message": "登录状态失效！"}), 401
    department = request.args.get('department')

    if not department:
        return jsonify({"message": "部门名称参数缺失"}), 400

    try:
        # 执行 SQL 查询
        g.cursor.execute('SELECT * FROM student WHERE department = %s', (department,))
        users = g.cursor.fetchall()  # 获取所有匹配的用户记录

        print(users)
        if not users:
            return jsonify({"message": "未找到该部门的用户"}), 404

        # 构造返回的 JSON 数据
        result = [{"student_id": user['student_id'], "name": user['name'],"tel": user['tel'],"role_in_depart": user['role_in_depart']} for user in users]
        return jsonify({"users": result}), 200

    except mariadb.Error as e:
        # 数据库错误处理
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

@admin.route('/add',methods=['POST'])
def add_user():
    if not session.get('session_id'):  # 更严格的校验
        return jsonify({"message": "登录状态失效！"}), 401
    try:
    #先获取各个信息
        student_id=request.json.get('student_id')
        name=request.json.get('name')
        department=request.json.get('department')
        role_in_depart=request.json.get('role_in_depart')
        tel=request.json.get('tel')
        password=student_id[-6:] # 密码默认使用学号后六位

        pswd_hash=hash_pswd(password)

        g.cursor.execute('INSERT INTO student (student_id,name,tel,department,role_in_depart,pswd_hash) VALUES (%s,%s,%s,%s,%s,%s)',(student_id,name,tel,department,role_in_depart,pswd_hash))
        return jsonify({"message":"添加成功"}),200
    except mariadb.Error as e:
        return jsonify({"error": f"数据库错误：{str(e)}","message":"请检查输入参数的内容和数量是否合法！"}), 500



@admin.route('/delete',methods=['POST'])
def delete_user():
    if not session.get('session_id'):  # 更严格的校验
        return jsonify({"message": "登录状态失效！"}), 401
    try:
        student_id=request.json.get('student_id')
        g.cursor.execute('DELETE FROM student WHERE student_id = %s', (student_id,))
        return jsonify({"message":"完成！"}),200
    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

@admin.route('/upload_excel',methods=['POST'])
def upload_excel():
    if not session.get('session_id'):  # 更严格的校验
        return jsonify({"message": "登录状态失效！"}), 401
    try:
        if 'file' not in request.files:
            return jsonify({"message": "未读取到文件"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"message": "未选中文件"}), 400

        if file.content_length > MAX_FILE_SIZE:
            return jsonify({"message": "文件大小不得大于10MB"}), 400

        now=datetime.now()
        format_time=now.strftime('%Y_%m_%d %H:%M:%S_')
        myfile_name = format_time+secure_filename(file.filename)
        file_path = os.path.join('app/upload/excel', myfile_name)

        file.save(file_path)
        excel_to_add=pd.read_excel(request.files['file'])
        expected_cols={"姓名":"name","电话":"tel","学号":"student_id","部门":"department","职位":"role_in_depart"}
        if not all(col in excel_to_add.columns for col in expected_cols.keys()):
            return jsonify({"error": "格式错误"}), 400
        excel_to_add=excel_to_add[list(expected_cols.keys())].rename(columns=expected_cols)
        insert_query="""INSERT INTO student (student_id,name,tel,department,role_in_depart) VALUES (%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                        name = VALUES(name),tel = VALUES(tel),department = VALUES(department),role_in_depart = VALUES(role_in_depart),
                        """
        data_to_insert = list(excel_to_add.itertuples(index=False, name=None))
        g.cursor.executemany(insert_query, data_to_insert)
        g.conn.commit()
        return jsonify({"message": "上传成功"}),200
    except mariadb.Error as e:
        return jsonify({"error": f"数据库错误：{str(e)}", "message": "请检查输入参数的内容和数量是否合法！"}), 500


