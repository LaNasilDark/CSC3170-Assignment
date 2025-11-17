# 后端API服务

## 🚀 快速启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制`.env.example`为`.env`并修改数据库密码：

```bash
cp .env.example .env
```

编辑`.env`文件：
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/dormitory_management_system
```

### 3. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --port 8000

# 或者使用Python直接运行
python -m app.main
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API说明

### 认证接口

- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/logout` - 用户登出

### 学生功能接口

- `GET /api/students/profile` - 查看个人信息
- `GET /api/students/dormitory` - 查看宿舍信息
- `GET /api/students/roommates` - 查看室友
- `GET /api/students/bills` - 查看账单
- `POST /api/students/dorm-change` - 提交宿舍调换申请
- `GET /api/students/dorm-change` - 查看宿舍调换申请
- `POST /api/students/maintenance` - 提交维修申请
- `GET /api/students/maintenance` - 查看维修申请
- `PUT /api/students/password` - 修改密码

## 🔑 测试账号

### 学生账号
- 用户名: `121090001` (任意学号)
- 密码: `123456`

### 管理员账号
- 用户名: `admin`
- 密码: `admin123`

## 📝 使用流程

1. 登录获取Token
2. 在后续请求的Header中携带Token: `Authorization: Bearer YOUR_TOKEN`
3. 调用相应的API接口

## 🛠️ 开发状态

✅ 已完成:
- 数据库连接和ORM模型
- JWT认证系统
- 学生功能API (9个)
- API自动文档

⏳ 待开发:
- 管理员功能API
- 更多业务逻辑完善
