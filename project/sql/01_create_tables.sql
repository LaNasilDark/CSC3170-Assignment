-- database: :memory:
-- ============================================================================
-- 宿舍管理系统 - 数据库表创建脚本
-- Database: dormitory_management_system
-- Version: 1.0
-- Date: 2025-11-17
-- ============================================================================

-- 删除已存在的表（如果存在）
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS maintenance_requests;
DROP TABLE IF EXISTS dorm_change_requests;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS dormitories;
DROP TABLE IF EXISTS administrators;

-- ============================================================================
-- 1. 学生表 (students)
-- ============================================================================
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY COMMENT '学号 (格式: 12x0y0abc)',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    gender ENUM('男', '女') NOT NULL COMMENT '性别',
    nationality VARCHAR(50) NOT NULL COMMENT '国籍',
    college VARCHAR(50) NOT NULL COMMENT '学院代码 (SSE/SME/MED/HSS/SAI/SDS/MUS)',
    enrollment_year INT NOT NULL COMMENT '入学年份',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱 (格式: 学号@cuhk.edu)',
    dorm_id INT COMMENT '宿舍ID (外键)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_gender (gender),
    INDEX idx_college (college),
    INDEX idx_enrollment_year (enrollment_year),
    INDEX idx_dorm_id (dorm_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生信息表';

-- ============================================================================
-- 2. 宿舍表 (dormitories)
-- ============================================================================
CREATE TABLE dormitories (
    dorm_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '宿舍ID',
    building_no VARCHAR(10) NOT NULL COMMENT '楼栋号 (MA/MB/MC/MD/FA/FB)',
    floor_no INT NOT NULL COMMENT '楼层号 (1-9)',
    room_no VARCHAR(20) NOT NULL UNIQUE COMMENT '房间号 (格式: MA101)',
    gender_type ENUM('男', '女') NOT NULL COMMENT '性别类型',
    total_beds INT NOT NULL DEFAULT 4 COMMENT '总床位数',
    occupied_beds INT NOT NULL DEFAULT 0 COMMENT '已占用床位数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_building_no (building_no),
    INDEX idx_gender_type (gender_type),
    INDEX idx_room_no (room_no),
    CHECK (occupied_beds <= total_beds),
    CHECK (occupied_beds >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='宿舍信息表';

-- ============================================================================
-- 3. 宿舍调换申请表 (dorm_change_requests)
-- ============================================================================
CREATE TABLE dorm_change_requests (
    request_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '申请ID',
    student_id VARCHAR(20) NOT NULL COMMENT '申请学生ID',
    current_dorm_id INT NOT NULL COMMENT '当前宿舍ID',
    target_dorm_id INT NOT NULL COMMENT '目标宿舍ID',
    reason TEXT COMMENT '申请理由',
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending' COMMENT '申请状态',
    admin_id INT COMMENT '处理管理员ID',
    admin_comment TEXT COMMENT '管理员备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_student_id (student_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (current_dorm_id) REFERENCES dormitories(dorm_id) ON DELETE CASCADE,
    FOREIGN KEY (target_dorm_id) REFERENCES dormitories(dorm_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='宿舍调换申请表';

-- ============================================================================
-- 4. 维修申请表 (maintenance_requests)
-- ============================================================================
CREATE TABLE maintenance_requests (
    request_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '申请ID',
    student_id VARCHAR(20) NOT NULL COMMENT '申请学生ID',
    dorm_id INT NOT NULL COMMENT '宿舍ID',
    issue_type VARCHAR(50) NOT NULL COMMENT '问题类型 (水电/家具/网络/其他)',
    description TEXT NOT NULL COMMENT '问题描述',
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') NOT NULL DEFAULT 'pending' COMMENT '处理状态',
    priority ENUM('low', 'medium', 'high', 'urgent') NOT NULL DEFAULT 'medium' COMMENT '优先级',
    admin_id INT COMMENT '处理管理员ID',
    admin_comment TEXT COMMENT '处理备注',
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_student_id (student_id),
    INDEX idx_dorm_id (dorm_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (dorm_id) REFERENCES dormitories(dorm_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维修申请表';

-- ============================================================================
-- 5. 账单表 (bills)
-- ============================================================================
CREATE TABLE bills (
    bill_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '账单ID',
    dorm_id INT NOT NULL COMMENT '宿舍ID',
    bill_type VARCHAR(50) NOT NULL COMMENT '账单类型 (住宿费/水费/电费/网费)',
    amount DECIMAL(10, 2) NOT NULL COMMENT '金额',
    billing_month VARCHAR(7) NOT NULL COMMENT '账单月份 (格式: 2024-09)',
    due_date DATE NOT NULL COMMENT '截止日期',
    status ENUM('unpaid', 'paid', 'overdue') NOT NULL DEFAULT 'unpaid' COMMENT '支付状态',
    paid_at TIMESTAMP NULL COMMENT '支付时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_dorm_id (dorm_id),
    INDEX idx_billing_month (billing_month),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date),
    FOREIGN KEY (dorm_id) REFERENCES dormitories(dorm_id) ON DELETE CASCADE,
    CHECK (amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账单表';

-- ============================================================================
-- 6. 管理员表 (administrators)
-- ============================================================================
CREATE TABLE administrators (
    admin_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '管理员ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    role ENUM('super_admin', 'admin', 'maintenance_staff') NOT NULL DEFAULT 'admin' COMMENT '角色',
    phone VARCHAR(20) COMMENT '电话',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';

-- ============================================================================
-- 添加外键约束
-- ============================================================================
ALTER TABLE students
    ADD CONSTRAINT fk_students_dorm 
    FOREIGN KEY (dorm_id) REFERENCES dormitories(dorm_id) 
    ON DELETE SET NULL;

ALTER TABLE dorm_change_requests
    ADD CONSTRAINT fk_dorm_change_admin 
    FOREIGN KEY (admin_id) REFERENCES administrators(admin_id) 
    ON DELETE SET NULL;

ALTER TABLE maintenance_requests
    ADD CONSTRAINT fk_maintenance_admin 
    FOREIGN KEY (admin_id) REFERENCES administrators(admin_id) 
    ON DELETE SET NULL;

-- ============================================================================
-- 创建视图 - 宿舍使用情况统计
-- ============================================================================
CREATE OR REPLACE VIEW v_dormitory_usage AS
SELECT 
    d.building_no AS '楼栋',
    d.gender_type AS '性别',
    COUNT(d.dorm_id) AS '总房间数',
    SUM(d.total_beds) AS '总床位数',
    SUM(d.occupied_beds) AS '已占用床位',
    SUM(d.total_beds) - SUM(d.occupied_beds) AS '空余床位',
    ROUND(SUM(d.occupied_beds) / SUM(d.total_beds) * 100, 2) AS '入住率(%)'
FROM dormitories d
GROUP BY d.building_no, d.gender_type
ORDER BY d.building_no;

-- ============================================================================
-- 创建视图 - 学生宿舍详情
-- ============================================================================
CREATE OR REPLACE VIEW v_student_dorm_info AS
SELECT 
    s.student_id AS '学号',
    s.name AS '姓名',
    s.gender AS '性别',
    s.college AS '学院',
    s.enrollment_year AS '入学年份',
    s.email AS '邮箱',
    d.room_no AS '宿舍房间号',
    d.building_no AS '楼栋',
    d.floor_no AS '楼层',
    d.occupied_beds AS '房间入住人数'
FROM students s
LEFT JOIN dormitories d ON s.dorm_id = d.dorm_id
ORDER BY s.student_id;

-- ============================================================================
-- 创建视图 - 待处理申请统计
-- ============================================================================
CREATE OR REPLACE VIEW v_pending_requests AS
SELECT 
    'dorm_change' AS '申请类型',
    COUNT(*) AS '待处理数量'
FROM dorm_change_requests
WHERE status = 'pending'
UNION ALL
SELECT 
    'maintenance' AS '申请类型',
    COUNT(*) AS '待处理数量'
FROM maintenance_requests
WHERE status = 'pending';

-- ============================================================================
-- 脚本完成
-- ============================================================================
