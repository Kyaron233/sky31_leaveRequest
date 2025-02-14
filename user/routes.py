import json
from asyncio import new_event_loop

import redis
from flask import Flask,request,session,jsonify,Blueprint,g
from werkzeug.utils import secure_filename
import uuid
import os
import mariadb


from packages import is_valid_pswd,hash_pswd,isPswdCorrect,convert_dict

#上传照片的参数
ALLOWED_EXTENSIONS = {'jpg,jpeg,png,webp,heic'}
MAX_FILE_SIZE = 1024*1024 * 10 # 10MB最大
MAX_CONTENT_LENGTH = MAX_FILE_SIZE

user_bp = Blueprint('user', __name__)
redis_client_user = redis.StrictRedis(host='redis', port=6379, db=1, decode_responses=True) # 使用与管理员不同的redis 数据库
SESSION_EXPIRY_TIME = 604800  # 7天

@user_bp.route('/login', methods=['POST'])
def login():
    # 登录接口优化，传递了“是否属于行政部”的参数

    student_id = request.json.get('student_id')
    password = request.json.get('password')

    if student_id is None or password is None:
        return jsonify({"message": "用户名或密码不能为空！"}), 401

    try:
        g.cursor.execute('select * from student where student_id=%s', (student_id,))
        stu=g.cursor.fetchone()
        if  stu is not None:
            if(isPswdCorrect(password,stu['pswd_hash'])):
                session_id = secrets.token_urlsafe(64)  # 随机生成 session_id

                # 将 session_id 和用户关联存储到 Redis 中，设置过期时间
                redis_client_user.set(session_id, stu['student_id'], ex=SESSION_EXPIRY_TIME)  # 键 值 过期时间

                # 将 session_id 存储在浏览器的 cookie 中
                response = make_response(jsonify({"message": "登录成功！"}), 200)
                response.set_cookie('session_id', session_id, max_age=SESSION_EXPIRY_TIME,
                                    secure=False)  # secure应在正式环境改成true

                return response
            else:
                return jsonify({"message": "用户名与密码不匹配！"}), 401
        else:
            return jsonify({"message": "找不到用户！"}), 401

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

# 用手机号鉴权
@user_bp.route('/update_pswd', methods=['POST'])
def update_pswd():
    session_id = request.json.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401

    student_id = request.json.get('student_id')

    g.cursor.execute('select * from student where student_id=%s', (student_id,))
    stu=g.cursor.fetchone()
    if request.json.get('tel') != stu['tel']:
        return jsonify({"message":"手机号错误，修改失败!"})

    new_pswd = request.json.get('new_pswd')
    if new_pswd is None:
        return jsonify({"message":"请输入新密码！"})
    if is_valid_pswd(new_pswd):
        pswd_hash = hash_pswd(new_pswd) # 生成新密码哈希 方法hash_pswd()得到的是一个字节字符串
    else:
        return jsonify({"message" : "密码不符合规则，请重新输入！"})


    try:
        g.cursor.execute("UPDATE student SET pswd_hash = %s WHERE student_id = %s ", (pswd_hash,student_id))
        g.db.commit()
        return jsonify({"message":"密码修改成功"})

    except mariadb.Error as e:
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500

@user_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session_id = request.cookies.get('session_id')  # 获取浏览器中的 session_id
    if session_id:
        # 删除 Redis 中的 session_id
        redis_client_user.delete(session_id)

    # 清除浏览器中的 session_id cookie
    response = make_response(jsonify({"message": "登出成功！"}), 200)
    response.delete_cookie('session_id')

    return response

@user_bp.route('/info', methods=['GET'])
# 用于“我的” 界面，获取用户信息
def info():
    #获取cookie中的session_id
    session_id = request.cookies.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401

    student_id = redis_client_user.get(session_id)

    try:
        g.cursor.execute("select * from student where student_id=%s",(student_id,))
        stu=g.cursor.fetchone()
        if stu is not None:
            return jsonify({"name":stu['name'],"student_id":stu['student_id'],"department":stu['department']}), 200
        else:
            return jsonify({"message": "未找到用户信息"}), 404

    except mariadb.Error as e:
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500

@user_bp.route('/main', methods=['GET'])
#主页

# 主页 显示所有正在进行的活动
def main():
    session_id = request.cookies.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401

    student_id = redis_client_user.get(session_id)


    try:
        # 获取当前登录的用户信息 根据部门、职位来返回事件
        g.cursor.execute("select * from student where student_id=%s",(student_id,))
        stu=g.cursor.fetchone()

        # 最多有七种类型的会议，用一个含有7个字典的列表来存,并使用counts_event计数


        # 获取全体事件，返回一个元组
        g.cursor.execute(""
                         "SELECT event_id,event_name,event_type,event_date,event_department "
                         "FROM events WHERE event_department = '全中心' AND isActive = 1")
        new_events=g.cursor.fetchall()
        events_to_return = new_events


        # 主席团例会
        if stu['department'] == "主席团" or stu['isPresent'] == 1:
            # 获取主席团事件，返回一个元组
            g.cursor.execute(""
                             "SELECT event_id,event_name,event_type,event_date,event_department"
                             " FROM events WHERE event_type = '主席团例会' AND isActive = 1")
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)


        # 部门大会
        if stu['department'] != "主席团":
            g.cursor.execute(""
                             "SELECT event_id,event_name,event_type,event_date,event_department "
                             "FROM events WHERE event_type = '部门大会' AND isActive = 1 AND event_department = %s",(stu['department'],))
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)

        # 部长级例会
        if stu['role_in_depart'] == "正部长" or stu['role_in_depart'] == "副部长" or stu['role_in_depart'] == "部门分管":
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department "
                "FROM events WHERE event_type = '部长级例会' AND isActive = 1 AND event_department = %s",
                (stu['department'],))
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)

        # 部长会议
        if stu['role_in_depart'] == "正部长" or stu['role_in_depart'] == "副部长" :
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department "
                "FROM events WHERE event_type = '部长会议' AND isActive = 1 AND event_department = %s",
                (stu['department'],))
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)

        # 部长干事会议
        if stu['department'] !=  "主席团" and stu['isPresent'] == 0 :
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department "
                "FROM events WHERE event_type = '部长干事会议' AND isActive = 1 AND event_department = %s",
                (stu['department'],))
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)

            # 按照event_id（即先后顺序）排序后返回
            events_to_return_sorted=sorted(events_to_return, key=lambda event: event['event_id'])
            return jsonify(events_to_return_sorted), 200

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误{str(e)}"}), 500



# 获取某事件的详细信息，填写请假表
@user_bp.route('/main/leaveRequest', methods=['POST'])
def leaveRequest():
    session_id=request.cookies.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401

    #获取登录的用户信息
    student_id = redis_client_user.get(session_id)
    g.cursor.execute("select * from student where student_id=%s",(student_id,))
    stu=g.cursor.fetchone()

    # 获取查询的事件名称，同时要注意：1.事件是否激活 2.是否是本部门的
    event_working=request.args.get('event_name')

    # 获取“是否需要照片”这一参数，前端传入1或者0，分别代表需要和不需要
    is_photos_needed=request.json.get('is_photos_needed')

    # 查找event_id
    try:
        g.cursor.execute("SELECT event_id from events WHERE isActive = 1 AND event_department = %s AND event_name =%s",(stu['department'],event_working))
        found_event_id=g.cursor.fetchone()

        if found_event_id is not None:
            return jsonify({"message":"未找到匹配的事件"})

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误{str(e)}"}), 500

    if is_photos_needed:
        # 在需要请假材料的情况下添加请假表
        try:
            reason=request.json.get('reason')

            # 上传图片
            # 检查是否有文件
            if 'files' not in request.files:
                return jsonify({"message": "未读取到文件"}), 400

            #以下都是传图片的代码
            files = request.files.getlist('files')  # 获取多个文件
            if not files or all(file.filename == '' for file in files):
                return jsonify({"message": "未选中文件"}), 400

            uploaded_files = []
            errors = []


            for file in files:
                if file.filename == '':
                    errors.append({"message": "未选中文件"})
                    continue

                # 计算文件大小
                file.seek(0, os.SEEK_END)  # 移动到文件流的末尾
                file_size = file.tell()  # 获取大小
                file.seek(0)  # 重置文件流到开头

                if file_size > MAX_FILE_SIZE:
                    errors.append({"message": f"文件 {file.filename} 大小不得大于10MB"})
                    continue

                # 生成唯一文件名,但是name是中文不知道会不会出错，待调试
                os.makedirs(f'app/upload/photos/{event_working}', exist_ok=True)
                now = datetime.now()
                format_time = now.strftime('%Y_%m_%d %H_%M_')
                myfile_name = format_time + stu['name']
                file_path = os.path.join(f'app/upload/photos/{event_working}', myfile_name) #事件名称作为一个文件夹放照片

                # 一次最多上传9张照片
                paths =["" for _ in range(9)]
                counts_photo = 0
                paths[counts_photo] = file_path
                counts_photo += 1


                # 保存文件
                file.save(file_path)
                uploaded_files.append({"filename": file.filename, "path": file_path})

            # 返回响应
                if errors:
                    return jsonify({"message": "部分文件上传失败", "errors": errors, "uploaded": uploaded_files}), 400

            paths_json = json.dumps(paths)
            #以上都是传图片的代码

            g.cursor.execute("INSERT INTO whoLeave "
                             "(whoLeave_event,whoLeave_id,whoLeave_name,related_event,leave_reason,photo_paths,photo_amount)"
                             "VALUES (%s, %s, %s, %s, %s, %s, %s)",event_working,stu['student_id'],stu['name'],found_event_id,reason,paths_json,counts_photo)

            return jsonify({"message": "文件上传成功", "uploaded": uploaded_files}), 200
        except mariadb.Error as e:
            return jsonify({"message": f"数据库错误：{str(e)}"}), 500

    else:
        # 在不需要请假材料的情况下添加请假表
        try:
            reason=request.json.get('reason')

            g.cursor.execute("INSERT INTO whoLeave "
                             "(whoLeave_event,whoLeave_id,whoLeave_name,related_event,leave_reason,photo_amount)"
                             "VALUES (%s, %s, %s, %s, %s, %s)", event_working, stu['student_id'], stu['name'],
                             found_event_id, reason,0)

            return jsonify({"message":"返回成功"}),200

        except mariadb.Error as e:
            return jsonify({"message": f"数据库错误：{str(e)}"}), 500


def user_login_valid(session_id):
    if not session_id or not valid_user_session_id(session_id):
        return False
    return True


def valid_user_session_id(session_id):
    user_id = redis_client_user.get(session_id)
    return user_id is not None  # 如果有值，说明会话有效