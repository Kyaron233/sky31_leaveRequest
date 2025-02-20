CREATE DATABASE IF NOT EXISTS sky31Employees;
FLUSH PRIVILEGES;

use sky31Employees;

create table if not exists admin(
    admin_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    pswd_hash VARCHAR(255) NOT NULL
);
create table if not exists student(
    student_id VARCHAR(255) NOT NULL UNIQUE,-- 学号 登录时的账号也就是学号
    name VARCHAR(255) NOT NULL,
    isPresident INT default 0, -- 意在标识是否属于主席团成员，部门为其分管的部门，其中主席团成员（团支书等）也标记为1
    tel VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    role_in_depart VARCHAR(255) NOT NULL,-- 存入职位的官方全称，团支书、正主席、部门分管、正部长、副部长、干事
    pswd_hash VARCHAR(255) NOT NULL,
    id INT AUTO_INCREMENT PRIMARY KEY -- 排序用

);


CREATE TABLE IF NOT EXISTS events(
    event_id INT AUTO_INCREMENT PRIMARY KEY, -- 事件的id，用于排序和表示
    event_name VARCHAR(255) not null, -- 事件名称
    event_type VARCHAR(255) NOT NULL,-- 事件类型
    event_date DATETIME,-- 事件预定的日期
    -- event_post_date DATETIME,-- 发布这篇请假请求的时间
    event_department VARCHAR(255) NOT NULL,-- 事件所属部门,全体事件标记为“全中心”
    is_photo_needed int not null,-- 是否需要照片
    isActive INT NOT NULL default 1 -- 事件的时效性，1表示正在进行，0表示已经过期
);
CREATE TABLE IF NOT EXISTS whoLeave(
    whoLeave_event VARCHAR(255),-- 对应请假的事件
    whoLeave_event_id INT NOT NULL,-- 对应event_id
    whoLeave_order INT AUTO_INCREMENT PRIMARY KEY,-- 请假者的次序，用于在用户提交针对同一事件的新请假表时，删除较久的请假表
    whoLeave_id INT NOT NULL, -- 学号
    whoLeave_name VARCHAR(255) NOT NULL,
    whoLeave_department VARCHAR(255) NOT NULL,-- 请假者的部门
    isActive INT NOT NULL default 1,-- 后面会有个触发器与event中同步

    leave_reason VARCHAR(255) NOT NULL,-- 请假原因
    check_opinion VARCHAR(255),-- 审批意见，可以是空值
    is_permitted INT DEFAULT 0,-- 通过与否，0代表未审批，1和-1分别代表同意和不同意
    check_time DATETIME,
    photo_paths VARCHAR(255), -- 由于要上传事实图片作为请假材料，故使用此变量记录服务器中上传的图片的位置,同时由于可以不上传图片，所以path可空
    photo_amount INT NOT NULL -- 不传照片则为0

);

INSERT INTO admin (admin_id,name,pswd_hash) VALUES ('admin','testAdmin',"$2b$12$mIz8BXciBPxDArvf4lNrhuPfIrwLkbFV0LrFR7M8br5MlXqwvg6Ee"); -- 密码是114514
INSERT INTO student(student_id,name,isPresident,tel,department,role_in_depart,pswd_hash) VALUES ( "202405134209","乌萨奇",0,"17680251526","技术研发部","干事","$2b$12$6hxSpCHa/QlzoQ/Vzv3eFuhn4jh92I8aZoYe5roS19hMKBOi2BAoS" );
DELIMITER $$

CREATE TRIGGER update_whoLeave_isActive_after_update_events
AFTER UPDATE ON events
FOR EACH ROW
BEGIN
    IF OLD.isActive <> NEW.isActive THEN
        UPDATE whoLeave
        SET isActive = NEW.isActive
        WHERE whoLeave_event_id = NEW.event_id;
    END IF;
END$$

DELIMITER ;


