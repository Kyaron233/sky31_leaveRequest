import json

from flask import Flask,request,session,jsonify,Blueprint,g
import logging
import sqlite3
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
                session['student_id'] = stu['student_id']
                session['name'] = stu['name']
                session['department'] = stu['department']
                is_XingZhengBu=True if stu['department'] == "行政部" else False
                return jsonify({"message":"登录成功","is_XingZhengBu":is_XingZhengBu}),200
            else:
                return jsonify({"message":"登录失败,密码错误"}),401
        else:
            return jsonify({"message":"不存在该用户"}),404

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

# 用手机号鉴权
@user_bp.route('/update_pswd', methods=['POST'])
def update_pswd():
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

    g.cursor.execute('select * from student where student_id=%s', (session['student_id'],))
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
        g.cursor.execute("UPDATE student SET pswd_hash = %s WHERE student_id = %s ", (pswd_hash,session['student_id']))
        g.db.commit()
        return jsonify({"message":"密码修改成功"})

    except mariadb.Error as e:
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500

@user_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('student_id', None)
    session.pop('name', None)
    return jsonify({"message": "账号已退出！"}), 200

@user_bp.route('/info', methods=['GET'])
# 用于“我的” 界面，获取用户信息
def info():
    # 检查用户是否登录
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

    student_id = session['student_id']

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
    # 登录状态检验
    if 'student_id' not in session:
        return jsonify({"message":"请先登录"}), 401
    try:
        # 获取当前登录的用户信息 根据部门、职位来返回事件
        g.cursor.execute("select * from student where student_id=%s",(session['student_id'],))
        stu=g.cursor.fetchone()

        # 最多有七种类型的会议，用一个含有7个字典的列表来存,并使用counts_event计数
        toReturnEvents = [{} for _ in range(7)]
        rawEvents = [{} for _ in range(7)]
        counts_events = 0

        # 获取全体事件，返回一个元组
        g.cursor.execute(""
                         "SELECT event_id,event_name,event_type,event_date,event_department "
                         "FROM events WHERE event_department = '全中心' AND isActive = 1")
        rawEvents[counts_events] = g.cursor.fetchall()

        # 转换元组成字典
        toReturnEvents[counts_events] = convert_dict(rawEvents[counts_events])
        counts_events += 1

        # 主席团例会
        if stu['department'] == "主席团" or stu['isPresent'] == 1:
            # 获取主席团事件，返回一个元组
            g.cursor.execute(""
                             "SELECT event_id,event_name,event_type,event_date,event_department"
                             " FROM events WHERE event_type = '主席团例会' AND isActive = 1")
            rawEvents[counts_events] = g.cursor.fetchall()

            # 转换元组成字典
            toReturnEvents[counts_events] = convert_dict(rawEvents[counts_events])
            counts_events += 1

        # 部门大会
        if stu['department'] != "主席团":
            g.cursor.execute(""
                             "SELECT event_id,event_name,event_type,event_date,event_department "
                             "FROM events WHERE event_type = '部门大会' AND isActive = 1 AND event_department = %s",(stu['department'],))
            rawEvents[counts_events] = g.cursor.fetchall()

            # 转换元组成字典
            toReturnEvents[counts_events] = convert_dict(rawEvents[counts_events])
            counts_events += 1

        # 部长级例会
        if stu['role_in_depart'] == "正部长" or stu['role_in_depart'] == "副部长" or stu['role_in_depart'] == "部门分管":
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department "
                "FROM events WHERE event_type = '部长级例会' AND isActive = 1 AND event_department = %s",
                (stu['department'],))
            rawEvents[counts_events] = g.cursor.fetchall()

            # 转换元组成字典
            toReturnEvents[counts_events] = convert_dict(rawEvents[counts_events])
            counts_events += 1

        # 部长会议
        if stu['role_in_depart'] == "正部长" or stu['role_in_depart'] == "副部长" :
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department "
                "FROM events WHERE event_type = '部长会议' AND isActive = 1 AND event_department = %s",
                (stu['department'],))
            rawEvents[counts_events] = g.cursor.fetchall()

            # 转换元组成字典
            toReturnEvents[counts_events] = convert_dict(rawEvents[counts_events])
            counts_events += 1

        # 部长干事会议
        if stu['department'] !=  "主席团" and stu['isPresent'] == 0 :
            g.cursor.execute(
                "SELECT event_id,event_name,event_type,event_date,event_department "
                "FROM events WHERE event_type = '部长干事会议' AND isActive = 1 AND event_department = %s",
                (stu['department'],))
            rawEvents[counts_events] = g.cursor.fetchall()

            # 转换元组成字典
            toReturnEvents[counts_events] = convert_dict(rawEvents[counts_events])
            counts_events += 1

            # 返回counts_events个字典
            return jsonify(toReturnEvents[:counts_events]), 200

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误{str(e)}"}), 500



# 获取某事件的详细信息，填写请假表
@user_bp.route('/main/leaveRequest', methods=['POST'])
def leaveRequest():

    # 检查登录状态
    if session['student_id'] is None:
        return ({"message":"未登录！"}),401

    # 获取查询的事件名称，同时要注意：1.事件是否激活 2.是否是本部门的
    event_working=request.args.get('event_name')

    # 查找event_id
    try:
        g.cursor.execute("SELECT event_id from events WHERE isActive = 1 AND event_department = %s AND event_name =%s",(session['department'],event_working))
        found_event_id=g.cursor.fetchone()

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误{str(e)}"}), 500

    # 提交请假表
    try:
        reason=request.json.get('reason')

        # 上传图片
        # 检查是否有文件
        if 'files' not in request.files:
            return jsonify({"message": "未读取到文件"}), 400

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
        g.cursor.execute("INSERT INTO whoLeave "
                         "(whoLeave_event,whoLeave_id,whoLeave_name,related_event,leave_reason,photo_paths,photo_amount)"
                         "VALUES (%s, %s, %s, %s, %s, %s, %s)",event_working,session['student_id'],session['name'],found_event_id,reason,paths_json,counts_photo)

        return jsonify({"message": "文件上传成功", "uploaded": uploaded_files}), 200

    except mariadb.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

# 历史、行政部的查看、发布、审批
import uuid
from flask import request, session, jsonify, Blueprint
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)

@user_bp.route('/apply_leave', methods=['POST'])
def apply_leave():
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

    event_id = request.form.get('event_id')
    reason = request.form.get('reason')

    if event_id is None:
        return jsonify({"message": "请提供活动 ID"}), 400

    try:
        event = Event.query.get(event_id)
        if event is None:
            return jsonify({"message": "未找到该活动"}), 404

        image = request.files.get('image')
        image_filename = None
        if image and allowed_file(image.filename):
            # 生成唯一的文件名
            filename = secure_filename(str(uuid.uuid4()) + '.' + image.filename.rsplit('.', 1)[1].lower())
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_filename = filename

        leave_application = LeaveApplication(
            student_id=session['student_id'],
            event_id=event.id,
            reason=reason,
            image_filename=image_filename
        )
        db.session.add(leave_application)
        db.session.commit()
        return jsonify({"message": "请假申请已提交"}), 200
    except sqlite3.Error as e:
        db.session.rollback()
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
@user_bp.route('/examine', methods=['GET'])
# 查看自己发布活动的请假列表


def examine():
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

@user_bp.route('/see_application', methods=['GET'])
def see_application():
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

    try:
        records=LeaveApplication.query.filter(LeaveApplication.student_name==session['name']).all()
        if records is None:
            return jsonify({"message":"暂无请假记录"})
        else:
            result = [{"event_name": record.event_name, "name": record.student_name, "department": record.student_department,"reason":record.reason} for record in records]

    except sqlite3.Error as e:
        db.session.rollback()
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500

@user_bp.route('/approve_leave/<int:application_id>', methods=['POST'])
def approve_leave(application_id):
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

    student_name = session['name']

    try:
        leave_application = LeaveApplication.query.get(application_id)
        if leave_application is None:
            return jsonify({"message": "未找到该请假申请"}), 404

        event = leave_application.event
        if event.publisher != student_name:
            return jsonify({"message": "你无权审批该请假申请"}), 403

        leave_application.status = 'approved'
        db.session.commit()
        return jsonify({"message": "请假申请已批准"}), 200
    except sqlite3.Error as e:
        db.session.rollback()
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500

@user_bp.route('/reject_leave/<int:application_id>', methods=['POST'])
def reject_leave(application_id):
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

    student_name = session['name']

    try:
        leave_application = LeaveApplication.query.get(application_id)
        if leave_application is None:
            return jsonify({"message": "未找到该请假申请"}), 404

        event = leave_application.event
        if event.publisher != student_name:
            return jsonify({"message": "你无权审批该请假申请"}), 403

        leave_application.status = 'rejected'
        db.session.commit()
        return jsonify({"message": "请假申请已拒绝"}), 200
    except sqlite3.Error as e:
        db.session.rollback()
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500