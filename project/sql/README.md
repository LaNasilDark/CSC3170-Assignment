# 宿舍管理系统 - SQL数据库脚本

## 📁 文件说明

### SQL脚本文件

- `01_create_tables.sql` - 创建数据库表结构
- `02_insert_data.sql` - 插入测试数据

## 🗄️ 数据库结构

### 表清单

#### 1. **students** - 学生表

- 存储学生基本信息和宿舍分配
- **主键**: `student_id` (学号)
- **外键**: `dorm_id` → dormitories(dorm_id)
- **记录数**: 4,354条

| 字段            | 类型         | 说明                               |
| --------------- | ------------ | ---------------------------------- |
| student_id      | VARCHAR(20)  | 学号 (格式: 12x0y0abc)             |
| password        | VARCHAR(255) | 密码 (默认: 123456)                |
| name            | VARCHAR(100) | 姓名                               |
| gender          | ENUM         | 性别 (男/女)                       |
| nationality     | VARCHAR(50)  | 国籍                               |
| college         | VARCHAR(50)  | 学院 (SSE/SME/MED/HSS/SAI/SDS/MUS) |
| enrollment_year | INT          | 入学年份                           |
| email           | VARCHAR(100) | 邮箱 (学号@cuhk.edu)               |
| dorm_id         | INT          | 宿舍ID                             |

#### 2. **dormitories** - 宿舍表

- 存储宿舍信息和入住情况
- **主键**: `dorm_id`
- **记录数**: 1,350间

| 字段          | 类型        | 说明                       |
| ------------- | ----------- | -------------------------- |
| dorm_id       | INT         | 宿舍ID (自增)              |
| building_no   | VARCHAR(10) | 楼栋号 (MA/MB/MC/MD/FA/FB) |
| floor_no      | INT         | 楼层号 (1-9)               |
| room_no       | VARCHAR(20) | 房间号 (如: MA206)         |
| gender_type   | ENUM        | 性别类型 (男/女)           |
| total_beds    | INT         | 总床位数 (4)               |
| occupied_beds | INT         | 已占用床位数               |

**宿舍配置**:

- 男生: 4栋 (A/B/C/D), 每栋9层, 每层25间 = 900间
- 女生: 2栋 (A/B), 每栋9层, 每层25间 = 450间

#### 3. **dorm_change_requests** - 宿舍调换申请表

- 存储学生宿舍调换申请
- **主键**: `request_id`
- **外键**: `student_id`, `current_dorm_id`, `target_dorm_id`, `admin_id`
- **测试数据**: 20条

| 字段            | 类型        | 说明                             |
| --------------- | ----------- | -------------------------------- |
| request_id      | INT         | 申请ID (自增)                    |
| student_id      | VARCHAR(20) | 申请学生ID                       |
| current_dorm_id | INT         | 当前宿舍ID                       |
| target_dorm_id  | INT         | 目标宿舍ID                       |
| reason          | TEXT        | 申请理由                         |
| status          | ENUM        | 状态 (pending/approved/rejected) |
| admin_id        | INT         | 处理管理员ID                     |
| admin_comment   | TEXT        | 管理员备注                       |

#### 4. **maintenance_requests** - 维修申请表

- 存储宿舍维修申请
- **主键**: `request_id`
- **外键**: `student_id`, `dorm_id`, `admin_id`
- **测试数据**: 15条

| 字段          | 类型        | 说明                                           |
| ------------- | ----------- | ---------------------------------------------- |
| request_id    | INT         | 申请ID (自增)                                  |
| student_id    | VARCHAR(20) | 申请学生ID                                     |
| dorm_id       | INT         | 宿舍ID                                         |
| issue_type    | VARCHAR(50) | 问题类型 (水电/家具/网络/其他)                 |
| description   | TEXT        | 问题描述                                       |
| status        | ENUM        | 状态 (pending/in_progress/completed/cancelled) |
| priority      | ENUM        | 优先级 (low/medium/high/urgent)                |
| admin_id      | INT         | 处理管理员ID                                   |
| admin_comment | TEXT        | 处理备注                                       |
| completed_at  | TIMESTAMP   | 完成时间                                       |

#### 5. **bills** - 账单表

- 存储宿舍相关账单
- **主键**: `bill_id`
- **外键**: `dorm_id`
- **测试数据**: 3,963条 (最近3个月)

| 字段          | 类型          | 说明                             |
| ------------- | ------------- | -------------------------------- |
| bill_id       | INT           | 账单ID (自增)                    |
| dorm_id       | INT           | 宿舍ID                           |
| bill_type     | VARCHAR(50)   | 账单类型 (住宿费/水费/电费/网费) |
| amount        | DECIMAL(10,2) | 金额                             |
| billing_month | VARCHAR(7)    | 账单月份 (如: 2024-09)           |
| due_date      | DATE          | 截止日期                         |
| status        | ENUM          | 支付状态 (unpaid/paid/overdue)   |
| paid_at       | TIMESTAMP     | 支付时间                         |

#### 6. **administrators** - 管理员表

- 存储管理员账号信息
- **主键**: `admin_id`
- **测试数据**: 3条

| 字段       | 类型         | 说明                                       |
| ---------- | ------------ | ------------------------------------------ |
| admin_id   | INT          | 管理员ID (自增)                            |
| username   | VARCHAR(50)  | 用户名                                     |
| password   | VARCHAR(255) | 密码                                       |
| name       | VARCHAR(100) | 姓名                                       |
| email      | VARCHAR(100) | 邮箱                                       |
| role       | ENUM         | 角色 (super_admin/admin/maintenance_staff) |
| phone      | VARCHAR(20)  | 电话                                       |
| is_active  | BOOLEAN      | 是否启用                                   |
| last_login | TIMESTAMP    | 最后登录时间                               |

## 👤 测试账号

### 管理员账号

| 用户名       | 密码       | 角色              | 说明       |
| ------------ | ---------- | ----------------- | ---------- |
| admin        | admin123   | super_admin       | 超级管理员 |
| dorm_manager | manager123 | admin             | 宿舍管理员 |
| maintenance  | maint123   | maintenance_staff | 维修人员   |

### 学生账号

- **所有学生默认密码**: `123456`
- **登录用户名**: 学号 (如: 121090001)
- **邮箱格式**: 学号@cuhk.edu (如: 121090001@cuhk.edu)

## 📊 数据统计

### 总体数据量

- 学生: 4,354 人 (男: 2,868, 女: 1,486)
- 宿舍: 1,350 间 (男: 900, 女: 450)
- 宿舍调换申请: 20 条
- 维修申请: 15 条
- 账单: 3,963 条 (2024年9-11月)
- 管理员: 3 个

### 宿舍入住情况

- 男生宿舍使用: 880间/900间 (约80%)
- 女生宿舍使用: 441间/450间 (约82%)
- 空余宿舍: 29间

## 🚀 使用方法

### 1. 创建数据库

```sql
CREATE DATABASE dormitory_management_system 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE dormitory_management_system;
```

### 2. 执行表创建脚本

```bash
mysql -u root -p dormitory_management_system < 01_create_tables.sql
```

### 3. 导入测试数据

```bash
mysql -u root -p dormitory_management_system < 02_insert_data.sql
```

**注意**: 数据插入脚本较大(约10MB),执行可能需要几分钟。

### 4. 验证数据

```sql
-- 查看各表记录数
SELECT 'students' AS table_name, COUNT(*) AS count FROM students
UNION ALL
SELECT 'dormitories', COUNT(*) FROM dormitories
UNION ALL
SELECT 'dorm_change_requests', COUNT(*) FROM dorm_change_requests
UNION ALL
SELECT 'maintenance_requests', COUNT(*) FROM maintenance_requests
UNION ALL
SELECT 'bills', COUNT(*) FROM bills
UNION ALL
SELECT 'administrators', COUNT(*) FROM administrators;
```

## 📈 预定义视图

### v_dormitory_usage - 宿舍使用情况统计

查看各楼栋的床位使用情况和入住率

```sql
SELECT * FROM v_dormitory_usage;
```

### v_student_dorm_info - 学生宿舍详情

查看学生的宿舍分配信息

```sql
SELECT * FROM v_student_dorm_info WHERE 学号 = '121090001';
```

### v_pending_requests - 待处理申请统计

查看待处理的宿舍调换和维修申请数量

```sql
SELECT * FROM v_pending_requests;
```

## 🔍 常用查询示例

### 查询某学生的信息

```sql
SELECT * FROM students WHERE student_id = '121090001';
```

### 查询某宿舍的入住学生

```sql
SELECT s.student_id, s.name, s.gender, s.college
FROM students s
WHERE s.dorm_id = (SELECT dorm_id FROM dormitories WHERE room_no = 'MA206');
```

### 查询未满的宿舍

```sql
SELECT room_no, gender_type, occupied_beds, total_beds
FROM dormitories
WHERE occupied_beds < total_beds
ORDER BY building_no, floor_no, room_no;
```

### 查询某学生的未支付账单

```sql
SELECT b.*
FROM bills b
JOIN students s ON b.dorm_id = s.dorm_id
WHERE s.student_id = '121090001' AND b.status = 'unpaid';
```

### 查询待处理的维修申请

```sql
SELECT mr.*, s.name AS student_name, d.room_no
FROM maintenance_requests mr
JOIN students s ON mr.student_id = s.student_id
JOIN dormitories d ON mr.dorm_id = d.dorm_id
WHERE mr.status = 'pending'
ORDER BY mr.priority DESC, mr.created_at ASC;
```

## 📝 数据库设计说明

### 索引策略

- 所有主键自动创建主键索引
- 外键字段创建普通索引以优化关联查询
- 高频查询字段(性别、学院、状态等)创建索引
- 时间字段创建索引以支持时间范围查询

### 约束设计

- 使用外键约束确保数据完整性
- CHECK约束确保床位数逻辑正确
- UNIQUE约束防止重复(邮箱、房间号等)
- NOT NULL约束保证必填字段

### 数据类型选择

- VARCHAR用于变长字符串(姓名、邮箱等)
- ENUM用于固定选项(性别、状态等)
- DECIMAL用于金额(精确计算)
- TIMESTAMP用于时间戳(自动更新)

---

**日期**: 2025-11-17
**数据库版本**: 1.0
**脚本兼容**: MySQL 8.0+
