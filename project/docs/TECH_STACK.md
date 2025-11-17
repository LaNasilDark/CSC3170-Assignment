# 宿舍管理系统 - Python技术栈方案

## 🎯 为什么选择Python

### ✅ 优势
1. **快速开发**: Python语法简洁，开发效率高，适合项目紧迫期限（6天）
2. **丰富的库**: Flask/FastAPI成熟的Web框架，SQLAlchemy强大的ORM
3. **易于学习**: 前后端代码更容易理解和维护
4. **符合要求**: 完全满足"前后端分离"和"不能直接访问数据库"的要求
5. **测试友好**: 已有大量Python测试数据生成脚本，可复用
6. **跨平台**: 部署简单，演示方便

### ⚠️ 注意事项
- 作业可能倾向于Java（CSC3170可能是数据库+Java课程）
- 需要确认是否允许使用Python
- 如果不确定，建议询问助教

## 🏗️ 推荐技术栈

### 后端 (Backend API)
```
Python 3.11+
├── FastAPI / Flask          # Web框架
│   ├── FastAPI (推荐)       # 现代、快速、自动生成API文档
│   └── Flask               # 轻量、灵活
├── SQLAlchemy              # ORM (对象关系映射)
├── PyMySQL / mysql-connector # MySQL数据库驱动
├── Pydantic                # 数据验证 (FastAPI内置)
├── python-jose[cryptography] # JWT认证
├── passlib[bcrypt]         # 密码加密
└── uvicorn                 # ASGI服务器 (FastAPI)
```

### 前端 (Frontend)
```
选项1: Web界面
├── HTML/CSS/JavaScript      # 基础技术
├── Bootstrap 5             # UI框架
├── jQuery / Fetch API      # HTTP请求
└── (可选) Vue.js/React     # 现代前端框架

选项2: CLI界面 (命令行)
├── Python                  # 
├── requests                # HTTP客户端
├── rich / click            # 美化CLI输出
└── tabulate                # 表格显示
```

### 数据库
```
MySQL 8.0+
```

## 📁 推荐项目结构

```
project/
├── backend/                    # 后端API服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── database.py        # 数据库连接配置
│   │   ├── models.py          # SQLAlchemy模型 (对应数据库表)
│   │   ├── schemas.py         # Pydantic模型 (请求/响应验证)
│   │   ├── crud.py            # 数据库操作 (增删改查)
│   │   ├── auth.py            # 认证授权
│   │   ├── dependencies.py    # 依赖注入
│   │   └── routers/           # API路由
│   │       ├── __init__.py
│   │       ├── students.py    # 学生相关API
│   │       ├── dormitories.py # 宿舍相关API
│   │       ├── requests.py    # 申请相关API
│   │       ├── bills.py       # 账单相关API
│   │       └── admin.py       # 管理员相关API
│   ├── requirements.txt       # Python依赖
│   ├── .env                   # 环境变量配置
│   └── README.md
│
├── frontend/                  # 前端界面
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── api.js         # API调用封装
│   │       ├── auth.js        # 认证逻辑
│   │       └── app.js         # 主应用逻辑
│   ├── templates/             # HTML模板
│   │   ├── index.html         # 登录页
│   │   ├── student/           # 学生界面
│   │   │   ├── dashboard.html
│   │   │   ├── profile.html
│   │   │   └── requests.html
│   │   └── admin/             # 管理员界面
│   │       ├── dashboard.html
│   │       ├── students.html
│   │       └── requests.html
│   └── README.md
│
├── sql/                       # 数据库脚本 (已完成)
│   ├── 01_create_tables.sql
│   ├── 02_insert_data.sql
│   └── README.md
│
├── data/                      # 测试数据 (已完成)
│   ├── students.xlsx
│   ├── dormitories.xlsx
│   └── students_final.xlsx
│
├── docs/                      # 项目文档
│   ├── API.md                # API接口文档
│   ├── DATABASE.md           # 数据库设计文档
│   └── report.md             # 项目报告
│
├── tests/                     # 测试文件
│   ├── test_api.py
│   └── test_database.py
│
├── requirements.txt           # 项目依赖
├── .env.example              # 环境变量模板
├── .gitignore
└── README.md                 # 项目说明
```

## 🎨 架构设计

### 三层架构
```
┌─────────────────────────────────────────┐
│          Frontend (前端)                 │
│  - HTML/CSS/JavaScript                  │
│  - 用户界面展示                          │
│  - 通过HTTP请求与后端API通信              │
└─────────────────┬───────────────────────┘
                  │ HTTP/HTTPS
                  │ (JSON数据)
┌─────────────────▼───────────────────────┐
│       Backend API (后端)                 │
│  - FastAPI/Flask                        │
│  - RESTful API接口                      │
│  - JWT认证授权                          │
│  - 业务逻辑处理                          │
└─────────────────┬───────────────────────┘
                  │ SQLAlchemy ORM
                  │ (SQL查询)
┌─────────────────▼───────────────────────┐
│       Database (数据库)                  │
│  - MySQL 8.0+                           │
│  - 数据持久化存储                         │
└─────────────────────────────────────────┘
```

### 关键点
- ✅ **前端不直接访问数据库**: 所有数据库操作通过后端API
- ✅ **RESTful API设计**: 标准的HTTP方法(GET/POST/PUT/DELETE)
- ✅ **JWT认证**: 基于Token的无状态认证
- ✅ **角色权限**: 学生和管理员不同权限
- ✅ **数据验证**: Pydantic自动验证请求数据

## 🔧 核心功能模块

### 1. 认证模块 (Authentication)
- 学生登录 (学号 + 密码)
- 管理员登录 (用户名 + 密码)
- JWT Token生成和验证
- 密码加密存储

### 2. 学生功能 (Student Role)
- 查看个人信息
- 查看宿舍信息
- 查看室友信息
- 提交宿舍调换申请
- 查看申请状态
- 提交维修申请
- 查看账单

### 3. 管理员功能 (Admin Role)
- 学生管理 (查询/修改)
- 宿舍管理 (查询/分配/调整)
- 申请处理 (审批/拒绝)
- 维修管理 (分配/跟踪)
- 账单管理 (生成/查询)
- 统计报表

## 🚀 快速开始

### 环境要求
- Python 3.11+
- MySQL 8.0+
- pip / conda

### 安装步骤

1. **创建虚拟环境**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. **安装依赖**
```bash
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt]
```

3. **配置数据库**
```bash
# 创建数据库
mysql -u root -p < sql/01_create_tables.sql
mysql -u root -p < sql/02_insert_data.sql
```

4. **配置环境变量** (.env)
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/dormitory_management_system
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. **启动后端服务**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

6. **访问API文档**
```
http://localhost:8000/docs  # Swagger UI
http://localhost:8000/redoc # ReDoc
```

## 📊 API设计示例

### 认证相关
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息

### 学生相关
- `GET /api/students/profile` - 查看个人信息
- `GET /api/students/dormitory` - 查看宿舍信息
- `GET /api/students/roommates` - 查看室友
- `GET /api/students/bills` - 查看账单

### 申请相关
- `POST /api/requests/dorm-change` - 提交宿舍调换申请
- `GET /api/requests/dorm-change` - 查看调换申请
- `POST /api/requests/maintenance` - 提交维修申请
- `GET /api/requests/maintenance` - 查看维修申请

### 管理员相关
- `GET /api/admin/students` - 查询学生列表
- `PUT /api/admin/students/{id}` - 修改学生信息
- `GET /api/admin/dormitories` - 查询宿舍列表
- `POST /api/admin/requests/{id}/approve` - 审批申请
- `POST /api/admin/requests/{id}/reject` - 拒绝申请

## 📝 开发建议

### 优先级
1. **高优先级**: 认证、学生查询、宿舍查询、申请提交
2. **中优先级**: 管理员功能、申请审批、账单管理
3. **低优先级**: 统计报表、高级搜索、数据导出

### 时间分配 (6天剩余)
- Day 1: 搭建项目结构 + 数据库连接 + 认证模块
- Day 2: 学生功能API + 基础前端页面
- Day 3: 管理员功能API + 管理界面
- Day 4: 申请处理功能 + 测试调试
- Day 5: 完善功能 + 撰写报告
- Day 6: 录制视频 + 最终检查

## ⚡ Python vs Java 对比

| 特性 | Python (FastAPI) | Java (Spring Boot) |
|------|------------------|-------------------|
| 开发速度 | ⭐⭐⭐⭐⭐ 快 | ⭐⭐⭐ 中等 |
| 学习曲线 | ⭐⭐⭐⭐⭐ 简单 | ⭐⭐⭐ 复杂 |
| 性能 | ⭐⭐⭐⭐ 好 | ⭐⭐⭐⭐⭐ 优秀 |
| API文档 | 自动生成 | 需配置Swagger |
| 类型安全 | 部分支持 | 完全支持 |
| 部署 | 简单 | 需要打包 |
| 适合场景 | 快速原型、中小项目 | 企业级、大型项目 |

## 🎓 最终建议

**如果时间紧迫且熟悉Python** → 使用Python + FastAPI ✅
**如果课程要求Java或需要企业级经验** → 使用Java + Spring Boot

**建议**: 先快速确认作业是否限制语言，如果不限制，Python是更快的选择！

---

是否继续使用Python？我可以立即开始创建项目结构！
