from flask import Flask,request,session,jsonify,Blueprint
from ..models import db, Student, Event, LeaveApplication
from ..password_utils import check,hashlize
import logging
import sqlite3
from werkzeug.utils import secure_filename
import uuid
import os
from ..models import allowed_file
from app import UPLOAD_FOLDER

user_bp = Blueprint('user', __name__)

logging.basicConfig(level=logging.INFO)

@user_bp.route('/login', methods=['POST'])
def login():
    student_id = request.json.get('student_id')
    password = request.json.get('password')

    if student_id is None or password is None:
        return jsonify({"message": "输入错误"}), 401

    try:
        stu=Student.query.get(int(student_id))
        if  stu is not None:
            if(check(password,stu.pswd_hash)):
                session['student_id'] = stu.student_id
                session['name'] = stu.name
                session['department'] = stu.department
                return jsonify({"message":"登录成功"}),200
            else:
                return jsonify({"message":"登录失败,密码错误"}),401
        else:
            return jsonify({"message":"不存在该用户"}),404

    except sqlite3.Error as e:
        return jsonify({"message": f"数据库错误：{str(e)}"}), 500

@user_bp.route('/update_pswd', methods=['POST'])
def update_pswd():
    if 'student_id' not in session:
        return jsonify({"message": "请先登录"}), 401

    new_pswd = request.json.get('new_pswd')
    pswd_hash = hashlize(new_pswd)
    pswd_hash =pswd_hash.decode('utf8')

    try:
        stu=Student.query.filter_by(student_id=session['student_id']).update({'pswd_hash':pswd_hash})
        db.session.commit()
        return jsonify({"message":"密码修改成功"})
    except sqlite3.Error as e:
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500

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

    student_id = session['student_id']

    try:
        info= Student.query.filter(Student.student_id==student_id).first()
        if info:
            return jsonify({"name":info.name,"student_id":info.student_id,"tel":info.tel,"department":info.department,"role_in_department":info.role_in_depart}), 200
        else:
            return jsonify({"message": "未找到用户信息"}), 404

    except sqlite3.Error as e:
        logging.error(f"数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500

@user_bp.route('/see_events', methods=['GET'])
#查看活动列表


def see_events():
    if 'student_id' not in session:
        return jsonify({"message":"请先登录"}), 401

    type=request.args.get('type')

    if type is None:
        return jsonify({"message":"类型错误"})
    else:
        try:
            events = Event.query.filter(Event.type==type).all()
            res=[{"event_name":i.name,"event_type":i.type,"time":i.datetime} for i in events]
            return jsonify({"events":res}), 200
        except sqlite3.Error as e:
            logging.error(f"数据库错误: {str(e)}")
            return jsonify({"message": f"数据库错误: {str(e)}"}), 500

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