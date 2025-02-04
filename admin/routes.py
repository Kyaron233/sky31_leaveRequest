from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash,session,jsonify
from myHash import hash_pswd,verify
from flask import g
import mariadb
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import pandas as pd


# 蓝图
admin = Blueprint('admin', __name__)
@admin.before_request
def before_request():
    #密码记得改回去
    g.conn = mariadb.connect(user='root',password='240700',host='localhost',database='sky31Employees')
    g.cursor = g.conn.cursor()

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

    if admin_id is None or password is None:
        return jsonify({"message": "输入错误"}), 401

    hashed_pswd=hash_pswd(password)
    try:
        g.cursor.execute('select * from admin where admin_id = %s AND pswd_hash = %s', (admin_id,hashed_pswd))
        user=g.cursor.fetchone()

        if user is not None:
            #登录成功
            session['admin_id'] = user[0]
            session['name'] = user[1]

            #这里应该要写重定向语句吧。。。。先写message
            #前端写重定向吧要不。。定位到管理员主页
            return jsonify({"message":"登陆成功"}),200
        else:
            return jsonify({"message": "输入错误"}), 401

    except mariadb.Error as e:
        #数据库错误
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500


@admin.route('/logout', methods=['POST','GET'])
#登出
def logout():
    session.pop('admin_id', None)
    session.pop('name', None)
    return jsonify({"message": "账号已退出！"}), 200

@admin.route('/query',methods=['GET'])
def query_user_by_department():
    if session.get('admin_id') is None:
        return jsonify({"message":"登录状态失效！"})
    department=request.args.get('department')

    if not department:
        return jsonify({"message": "部门名称参数缺失"}), 400

    try:
        # 执行 SQL 查询
        g.cursor.execute('SELECT * FROM student WHERE department = %s', (department))
        users = g.cursor.fetchall()  # 获取所有匹配的用户记录

        if not users:
            return jsonify({"message": "未找到该部门的用户"}), 404

        # 构造返回的 JSON 数据
        result = [{"id": user[0], "name": user[1], "department": user[2]} for user in users]
        return jsonify({"users": result}), 200

    except mariadb.Error as e:
        # 数据库错误处理
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

@admin.route('/add',methods=['POST'])
def add_user():

    #先获取各个信息
    student_id=request.json.get('student_id')
    name=request.json.get('name')
    department=request.json.get('department')
    role_in_depart=request.json.get('role_in_depart')
    tel=request.json.get('tel')
    password=request.json.get('password')

    pswd_hash=hash_pswd(password)

    g.cursor.execute('INSERT INTO student (student_id,name,tel,department,role_in_depart,pswd_hash) VALUES (%s,%s,%s,%s,%s,%s)',(student_id,name,tel,department,role_in_depart,pswd_hash))

@admin.route('/delete',methods=['POST'])
def delete_user():
    student_id=request.json.get('student_id')
    g.cursor.execute('DELETE FROM student WHERE student_id = %s', (student_id))

@admin.route('/upload_excel',methods=['POST'])
def upload_excel():
    print(request.files)
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
    file_path = os.path.join('./uploads', myfile_name)

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
    return jsonify({"message": "上传成功"})

