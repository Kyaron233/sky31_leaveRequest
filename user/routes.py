import json
from asyncio import new_event_loop
from datetime import datetime

import redis
from flask import Flask,request,session,jsonify,Blueprint,g,make_response
from werkzeug.utils import secure_filename
import uuid
import os
import mariadb
import secrets

import user
from packages import is_valid_pswd,hash_pswd,isPswdCorrect,convert_dict,role_in_depart_mapping,department_mapping

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
        return jsonify({"message":"密码修改成功"})

    except mariadb.Error as e:
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
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500


# 主页 显示所有的活动
@user_bp.route('/main', methods=['GET'])
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


        # 获取全体事件
        g.cursor.execute(""
                         "SELECT event_id,event_name,event_type,event_date,event_department,isActive "
                         "FROM events WHERE event_department = '全中心' AND isActive=1 ")
        new_events=g.cursor.fetchall()
        events_to_return = new_events


        # 主席团例会
        if stu['department'] == "主席团" or stu['isPresident'] == 1:
            # 获取主席团事件，返回一个元组
            g.cursor.execute(""
                             "SELECT event_id,event_name,event_type,event_date,event_department,isActive "
                             " FROM events WHERE event_type = '主席团例会' AND isActive=1 ")
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)


        # 部门大会
        if stu['department'] != "主席团":
            g.cursor.execute(""
                             "SELECT event_id,event_name,event_type,event_date,event_department,isActive "
                             "FROM events WHERE event_type = '部门大会' AND event_department = %s ",(stu['department'],))
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)

        # 部长级例会
        if stu['role_in_depart'] == "正部长" or stu['role_in_depart'] == "副部长" or stu['role_in_depart'] == "分管主席":
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department,isActive "
                "FROM events WHERE event_type = '部长级例会'AND event_department = %s ",
                (stu['department'],))
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)

        # 部长会议
        if stu['role_in_depart'] == "正部长" or stu['role_in_depart'] == "副部长" :
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department,isActive "
                "FROM events WHERE event_type = '部长会议'  AND event_department = %s ",
                (stu['department'],))
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)

        # 部长干事会议
        if stu['department'] !=  "主席团" and stu['isPresident'] == 0 :
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department,isActive "
                "FROM events WHERE event_type = '部长干事会议'  AND event_department = %s ",
                (stu['department'],))
            new_events = g.cursor.fetchall()
            events_to_return.extend(new_events)

            # 到时候看下排序前需不需要格式化时间
            # 按照event_date（即先后顺序）排序后返回
            events_to_return_sorted = sorted(events_to_return, key=lambda x: x['event_date'],reverse=True) # event_date,反过来排序，时间越晚越靠前

            # 遍历列表，找到第一个时间超过当前时间的事件
            for index, event in enumerate(events_to_return_sorted):
                event_time = datetime.strptime(event['event_date'], '%Y-%m-%d %H:%M:%S',)  # 根据日期时间格式进行解析
                if event['isActive'] == 0: # 说明事件已经被标记为过期，那么后续事件也已经被标记为过期,此时则不需要执行
                    break

                # 找到过期时间，因为排序了所以从找到的第一个过期的事件
                if event_time < datetime.now():
                    for subsequent_event in events_to_return_sorted[index:]:
                        if subsequent_event['isActive'] == 0: #找到过期时间后break
                            break
                        subsequent_event['isActive']=0
                        subsequent_invalid_id = subsequent_event['event_id']
                        g.cursor.execute(
                            "UPDATE events SET isActive = 0 WHERE isActive = 1 AND event_id = %s",
                            (subsequent_invalid_id,)
                        )
            return jsonify(events_to_return_sorted), 200

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误{str(e)}"}), 500

# 传入event_id 检查是否已有提交记录
@user_bp.route('/main/leaveRequest/<int:event_id>', methods=['GET'])
def query_leaveRequest(event_id):
    session_id = request.cookies.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401
    student_id = redis_client_user.get(session_id)
    g.cursor.execute("select whoLeave_event,whoLeave_id,whoLeave_name,leave_reason,photo_paths,photo_amount,is_permitted,check_opinion from whoLeave where student_id=%s and whoLeave_event_id",(student_id,event_id))
    event = g.cursor.fetchone()
    if event is None:
        return jsonify({"message":"此事件未填写请假表"})
    else:
        # 根据有没有照片定义行为,这是没有照片
        if event['photo_amount']:
            return jsonify({"event":event['whoLeave_event'],
                            "whoLeave_id":event['whoLeave_id'],
                            "whoLeave_name":event['whoLeave_name'],
                            "whoLeave_reason":event['whoLeave_reason'],
                            'is_permitted':event['is_permitted'],
                            'check_opinion':event['check_opinion'],}),
        else: #这是要返回照片的 到时候再写


# 获取某事件的详细信息，填写请假表
@user_bp.route('/main/leaveRequest/<int:event_id>', methods=['POST'])
def leaveRequest(event_id):
    session_id=request.cookies.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401

    #获取登录的用户信息
    student_id = redis_client_user.get(session_id)
    g.cursor.execute("select * from student where student_id=%s",(student_id,))
    stu=g.cursor.fetchone()


    # 获取“是否需要照片”这一参数，并获取事件名称
    g.cursor.execute("select is_photo_needed ,event_name from event where event_id=%s",(event_id,))
    temp=g.cursor.fetchone()
    is_photo_needed=temp['is_photo_needed']
    event_name=temp['event_name']

    # 查找event_id
    try:
        g.cursor.execute("SELECT * from events WHERE isActive = 1 AND (event_department = %s OR event_department = ‘全中心’) AND event_id =%s",(stu['department'],event_id))
        found_event=g.cursor.fetchone()

        if found_event is not None:
            return jsonify({"message":"未找到匹配的事件"})

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误{str(e)}"}), 500

    if is_photo_needed:
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


            errors = []

            counts_photo = 0

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
                # 要注意文件夹不能正确创建等问题
                os.makedirs(f'app/upload/photos/{event_id}', exist_ok=True)
                now = datetime.now()
                format_time = now.strftime('%Y_%m_%d %H_%M_')
                myfile_name = format_time + ' ' + stu['name']
                file_path = os.path.join(f'app/upload/photos/{event_id}', myfile_name) #事件id作为一个文件夹放照片

                # 一次最多上传3张照片，前端拦截掉超过3张照片的请求
                paths =["" for _ in range(3)]

                paths[counts_photo] = file_path
                counts_photo += 1


                # 保存文件
                file.save(file_path)


            # 返回响应
                if errors:
                    return jsonify({"message": "部分文件上传失败", "errors": errors, "uploaded": uploaded_files}), 400

            paths_json = json.dumps(paths)
            #以上都是传图片的代码

            g.cursor.execute("INSERT INTO whoLeave "
                             "(whoLeave_event,whoLeave_event_id,whoLeave_id,whoLeave_name,leave_reason,photo_paths,photo_amount)"
                             "VALUES (%s, %s , %s , %s, %s, %s, %s)",event_name,event_id,stu['student_id'],stu['name'],reason,paths_json,counts_photo)

            return jsonify({"message": "文件上传成功"}), 200
        except mariadb.Error as e:
            return jsonify({"message": f"数据库错误：{str(e)}"}), 500

    else:
        # 在不需要请假材料的情况下添加请假表
        try:
            reason=request.json.get('reason')

            g.cursor.execute("INSERT INTO whoLeave "
                             "(whoLeave_event,whoLeave_event_id,whoLeave_id,whoLeave_name,leave_reason,photo_amount)"
                             "VALUES (%s, %s, %s, %s, %s, %s, %s)",event_name, event_id, stu['student_id'], stu['name'],
                             reason,0)

            return jsonify({"message":"返回成功"}),200

        except mariadb.Error as e:
            return jsonify({"message": f"数据库错误：{str(e)}"}), 500

# 获取历史事件的概要 给行政用
# 获取详情（包括照片等内容的时候）调用查询接口
# 按照学号查询
@user_bp.route('/query/history/student/<int:student_id>', methods=['GET'])
def queryHistory(student_id):
    session_id=request.cookies.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401

    g.cursor.execute('select event_name,leave_reason,check_opinion,is_permitted,check_time from whoLeave where whoLeave_id = %s',(student_id,))
    events=g.cursor.fetchall()

    # 按时间排序 到时候看下排序前需不需要格式化时间
    events_sorted = sorted(events, key=lambda x: x['check_time'], reverse=True)
    return jsonify(events_sorted), 200

# 按照部门查询
@user_bp.route('/query/history/department/<str:department_id>', methods=['GET'])
def queryHistoryByDepartment(department_id):
    session_id=request.cookies.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401

    department=department_mapping.get(department_id)

    g.cursor.execute('select event_name,leave_reason,check_opinion,is_permitted,check_time from whoLeave where whoLeave_department = %s',(department,))
    events=g.cursor.fetchall()

    #到时候看下排序前需不需要格式化时间
    events_sorted = sorted(events, key=lambda x: x['check_time'], reverse=True)
    return jsonify(events_sorted), 200


#这里也忘记加返回照片了
@user_bp.route('/query/history/self', methods=['GET'])
def queryHistory_self():
    session_id=request.cookies.get('session_id')
    if not user_login_valid(session_id):
        return jsonify({"message": "登录状态失效！"}), 401

    student_id=redis_client_user.get(session_id)
    g.cursor.execute('select event_name,leave_reason,check_opinion,ispermitted,check_time from whoLeave where whoLeave_id = %s',(student_id,))
    events=g.cursor.fetchall()

    #到时候看下排序前需不需要格式化时间
    events_sorted = sorted(events, key=lambda x: x['check_time'], reverse=True)
    return jsonify(events_sorted), 200



def user_login_valid(session_id):
    if not session_id or not valid_user_session_id(session_id):
        return False
    return True


def valid_user_session_id(session_id):
    user_id = redis_client_user.get(session_id)
    return user_id is not None  # 如果有值，说明会话有效