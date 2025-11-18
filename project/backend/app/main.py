"""
FastAPI主应用
宿舍管理系统后端API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .routers import auth, students, admin

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title=os.getenv("APP_NAME", "Dormitory Management System"),
    description="宿舍管理系统后端API - 支持学生和管理员功能",
    version=os.getenv("APP_VERSION", "1.0.0"),
    docs_url="/docs",  # Swagger UI文档地址
    redoc_url="/redoc"  # ReDoc文档地址
)

# 配置CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(admin.router)

# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """
    API根路径 - 返回系统信息
    """
    return {
        "message": "宿舍管理系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
