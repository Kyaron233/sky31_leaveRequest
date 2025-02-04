CREATE USER 'root'@'localhost' IDENTIFIED BY 'sky31admin';
CREATE DATABASE IF NOT EXISTS sky31Employees;
GRANT ALL PRIVILEGES ON sky31Employees.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;

use sky31Emplyees;

create table if not exists admin(
    admin_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    pswd_hash VARCHAR(255) NOT NULL
)
create table if not exists student( --记住没用复数。。。。
    student_id VARCHAR(255) NOT NULL,--学号 登录时的账号也就是学号
    name VARCHAR(255) NOT NULL,
    tel VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,--id是不是没啥必要。。或者说部门名称是不是没啥必要。。
    role_in_depart VARCHAR(255) NOT NULL,--下面那个方案废弃，。。。。
    --如果没记错的话，部门内只有正部、副部、干事三个职位，职位等级依次递减，那么我们用0，1，2分别标志这三个职位
    pswd_hash VARCHAR(255) NOT NULL,
    id INT AUTO_INCREMENT PRIMARY KEY

);


CREATE TABLE IF NOT EXISTS events(
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(255) AUTO_INCREMENT PRIMARY KEY,
    event_date DATETIME
);
CREATE TABLE IF NOT EXISTS whoLeave(
    whoLeave_order INT AUTO_INCREMENT PRIMARY KEY,--请假者的次序
    whoLeave_id INT NOT NULL,
    whoLeave_name VARCHAR(255) NOT NULL,

    leave_reason VARCHAR(255) NOT NULL,--请假原因
    check_opinion VARCHAR(255) ,--审批意见，可以是空值
    is_permitted INT DEFAULT 0,--通过与否，0代表未审批，1和-1分别代表同意和不同意
    check_time DATETIME,
    path_to_image VARCHAR(255)--由于要上传事实图片作为请假材料，故使用此变量记录服务器中上传的图片的位置
    --记得写上传图片的接口。。。。。
);


