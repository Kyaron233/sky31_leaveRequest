from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash,session,jsonify
from myHash import hash_pswd,verify
from flask import g
import mariadb


admin = Blueprint('admin', __name__)
@admin.before_request
def before_request():
    g.conn = mariadb.connect(user='root',password='sky31admin',host='localhost',database='sky31Employees')
    g.cursor = g.conn.cursor()

#管理员需要的接口：登录，查询，增加，删除，退出登录，
#查询应该还要细分一下：按部门查询
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
            session['admin'] = user[0]
            session['name'] = user[1]

            #这里应该要写重定向语句吧。。。。先写message
            #前端写重定向吧要不。。定位到管理员主页
            return jsonify({"message":"登陆成功"}),200
        else:
            return jsonify({"message": "输入错误"}), 401

    except mariadb.Error as e:
        #数据库错误
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500


@admin.route('/logout')
#登出
def logout():
    session.pop('admin', None)
    session.pop('name', None)
    return jsonify({"message": "账号已退出！"}), 200

@admin.route('/query',methods=['GET'])
def query_user_by_department():
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

@admin.route('/upload_excel')
def upload_excel():

@admin.route('/add_more',methods=['POST'])
def add_more():
