from flask import Blueprint, request, session,jsonify,make_response
from packages import hash_pswd,isPswdCorrect,role_in_depart_mapping,department_mapping
from flask import g
import mariadb
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import secrets
import pandas as pd
import redis


# 蓝图
admin = Blueprint('admin', __name__)



MAX_FILE_SIZE = 1024*1024 * 10 # 10MB表格最大
MAX_CONTENT_LENGTH = MAX_FILE_SIZE

# 使用redis管理session
redis_client_admin = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)
# 设置会话过期时间
SESSION_EXPIRY_TIME = 604800  # 7天

@admin.route('/login', methods=['POST'])
#登录
def login():
    admin_id=request.json.get('admin_id')
    password=request.json.get('password')
    if admin_id is None or password is None:
        return jsonify({"message":"用户名或密码不能为空"})

    try:
        g.cursor.execute('select * from admin where admin_id = %s', (admin_id,))
        user=g.cursor.fetchone()

        if user is not None:
            if isPswdCorrect(password,user['pswd_hash']): # 密码正确与否
                session_id = secrets.token_urlsafe(64)  # 随机生成 session_id

                # 将 session_id 和用户关联存储到 Redis 中，设置过期时间
                redis_client_admin.set(session_id, user['admin_id'], ex=SESSION_EXPIRY_TIME) # 键 值 过期时间

                # 将 session_id 存储在浏览器的 cookie 中
                response = make_response(jsonify({"message": "登录成功！"}), 200)
                response.set_cookie('session_id', session_id, max_age=SESSION_EXPIRY_TIME,secure=False) # secure应在正式环境改成true

                return response
            else:
                return jsonify({"message": "用户名与密码不匹配！"}), 401
        else :
            return jsonify({"message": "找不到用户！"}), 401

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500


@admin.route('/logout', methods=['POST'])
def logout():
    session_id = request.cookies.get('session_id')  # 获取浏览器中的 session_id
    if session_id:
        # 删除 Redis 中的 session_id
        redis_client_admin.delete(session_id)

    # 清除浏览器中的 session_id cookie
    response = make_response(jsonify({"message": "登出成功！"}), 200)
    response.delete_cookie('session_id')

    return response

@admin.route('/query',methods=['GET'])
def query_user_by_department():
    if not admin_login_valid(request.cookies.get('session_id')):
        return jsonify({"message": "登录状态失效！"}), 401

    # 进行部门参数映射
    department = department_mapping.get(request.args.get('department'))

    if not department:
        return jsonify({"message": "部门名称参数缺失"}), 400



    try:
        # 执行 SQL 查询
        g.cursor.execute('SELECT * FROM student WHERE department = %s', (department,))
        users = g.cursor.fetchall()  # 获取所有匹配的用户记录

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
    if not admin_login_valid(request.cookies.get('session_id')):
        return jsonify({"message": "登录状态失效！"}), 401

    try:
    #先获取各个信息
        student_id=request.json.get('student_id')
        name=request.json.get('name')
        department=department_mapping.get(request.json.get('department'))
        role_in_depart=role_in_depart_mapping.get(request.json.get('role_in_depart'))
        tel=request.json.get('tel')
        password=student_id[-6:] # 密码默认使用学号后六位

        pswd_hash=hash_pswd(password)

        g.cursor.execute('INSERT INTO student (student_id,name,tel,department,role_in_depart,pswd_hash) VALUES (%s,%s,%s,%s,%s,%s)',(student_id,name,tel,department,role_in_depart,pswd_hash))
        g.cursor.execute('UPDATE student SET isPresent = 1 WHERE role_in_depart = %s', ("部门主管",))
        return jsonify({"message":"添加成功"}),200
    except mariadb.Error as e:
        return jsonify({"error": f"数据库错误：{str(e)}","message":"请检查输入参数的内容和数量是否合法！"}), 500



@admin.route('/delete',methods=['POST'])
def delete_user():
    if not admin_login_valid(request.cookies.get('session_id')):
        return jsonify({"message": "登录状态失效！"}), 401
    try:
        student_id=request.json.get('student_id')
        g.cursor.execute('DELETE FROM student WHERE student_id = %s', (student_id,))
        return jsonify({"message":"完成！"}),200
    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

@admin.route('/upload_excel',methods=['POST'])
def upload_excel():
    if not admin_login_valid(request.cookies.get('session_id')):
        return jsonify({"message": "登录状态失效！"}), 401
    try:
        if 'file' not in request.files:
            return jsonify({"message": "未读取到文件"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"message": "未选中文件"}), 400


        # 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({"message": "文件格式错误，必须是 Excel 文件"}), 400

        if file.content_length > MAX_FILE_SIZE:
            return jsonify({"message": "文件大小不得大于10MB"}), 400

        #检查文件夹是否存在
        UPLOAD_FOLDER='app/upload/excel'
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        #构建文件名
        now=datetime.now()
        format_time=now.strftime('%Y_%m_%d %H:%M:%S_')
        myfile_name = format_time+secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, myfile_name)

        file.save(file_path)
        excel_to_add=pd.read_excel(file_path)

        expected_cols={"姓名":"name","电话":"tel","学号":"student_id","部门":"department","职位":"role_in_depart"}
        # 验证 Excel 文件中的列名是否与期望的列名一致
        if not all(col in excel_to_add.columns for col in expected_cols.keys()):
            missing_cols = [col for col in expected_cols.keys() if col not in excel_to_add.columns]
            return jsonify({"error": f"格式错误：缺少必要的列 - {', '.join(missing_cols)}"}), 400

        # 重排列的顺序以确保一致性
        excel_to_add = excel_to_add[expected_cols.keys()]


        #处理电话、学号是int而不是字符串的情况
        excel_to_add['学号'] = excel_to_add['学号'].astype(str)
        excel_to_add['电话'] = excel_to_add['电话'].astype(str)

        # 重命名 使列名与数据库的相匹配
        excel_to_add=excel_to_add[list(expected_cols.keys())].rename(columns=expected_cols)

        # 提取学号的后六位并创建新列
        excel_to_add['last_num'] = excel_to_add['student_id'].apply(lambda x: x[-6:])

        # 调用 hash_pswd()
        excel_to_add['last_num'] = excel_to_add['last_num'].apply(hash_pswd)

        insert_query="""INSERT INTO student (name,tel,student_id,department,role_in_depart,pswd_hash) VALUES (%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                        name = VALUES(name),tel = VALUES(tel),department = VALUES(department),role_in_depart = VALUES(role_in_depart)
                        """
        data_to_insert = list(excel_to_add.itertuples(index=False, name=None))
        g.cursor.executemany(insert_query, data_to_insert)
        g.cursor.execute('UPDATE student SET isPresent = 1 WHERE role_in_depart = %s', ("部门主管",))
        g.conn.commit()
        return jsonify({"message": "上传成功"}),200
    except mariadb.Error as e:
        return jsonify({"error": f"数据库错误：{str(e)}", "message": "请检查输入参数的内容和数量是否合法！"}), 500

@admin.route('/delete/anything', methods=['GET'])
def delete_all():
    if not admin_login_valid(request.cookies.get('session_id')):
        return jsonify({"message": "登录状态失效！"}), 401
    try:
        g.cursor.execute('TRUNCATE TABLE student')
        g.cursor.execute('TRUNCATE TABLE whoLeave')
        g.cursor.execute('TRUNCATE TABLE events')
        return jsonify({"message": "所有数据已成功删除！"}), 200
    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

def admin_login_valid(session_id):
    if not session_id or not valid_admin_session_id(session_id):
        return False
    return True


def valid_admin_session_id(session_id):
    user_id = redis_client_admin.get(session_id)
    return user_id is not None  # 如果有值，说明会话有效
