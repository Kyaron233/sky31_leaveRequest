CREATE USER 'root'@'localhost' IDENTIFIED BY 'sky31admin';
CREATE DATABASE IF NOT EXISTS sky31Employees;
GRANT ALL PRIVILEGES ON sky31Employees.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;

use sky31Emplyees;

create table if not exists admin(
    admin_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    pswd_hash VARCHAR(255) NOT NULL
);
create table if not exists student(
    student_id VARCHAR(255) NOT NULL UNIQUE,--学号 登录时的账号也就是学号
    name VARCHAR(255) NOT NULL,
    tel VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,-
    role_in_depart VARCHAR(255) NOT NULL,--存入职位的官方全称
    pswd_hash VARCHAR(255) NOT NULL,
    id INT AUTO_INCREMENT PRIMARY KEY

);


CREATE TABLE IF NOT EXISTS events(
    event_id INT AUTO_INCREMENT PRIMARY KEY, --事件的id
    event_name VARCHAR(255) AUTO_INCREMENT PRIMARY KEY not null, --事件名称
    event_type VARCHAR(255) NOT NULL,--事件类型
    event_date DATETIME,--事件预定的日期
    event_post_date DATETIME,--发布这篇请假请求的时间
    event_sight_sort VARCHAR(255) --设置事件的可见性，默认值就是当前发布者登录的账号所属于的部门，其他人在搜索的时候按部门搜索，用“全局”代表所有人都能查看
);
CREATE TABLE IF NOT EXISTS whoLeave(
    whoLeave_event VARCHAR(255),--对应请假的事件
    whoLeave_order INT AUTO_INCREMENT PRIMARY KEY,--请假者的次序
    whoLeave_id INT NOT NULL, --学号
    whoLeave_name VARCHAR(255) NOT NULL,

    leave_reason VARCHAR(255) NOT NULL,--请假原因
    check_opinion VARCHAR(255) ,--审批意见，可以是空值
    is_permitted INT DEFAULT 0,--通过与否，0代表未审批，1和-1分别代表同意和不同意
    check_time DATETIME,
    path_to_image VARCHAR(255)--由于要上传事实图片作为请假材料，故使用此变量记录服务器中上传的图片的位置
    --记得写上传图片的接口。。。。。
);


