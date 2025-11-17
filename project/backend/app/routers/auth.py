"""
认证相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from .. import schemas, auth, models
from ..database import get_db

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=schemas.Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口（学生或管理员）
    
    - **username**: 学号（学生）或用户名（管理员）
    - **password**: 密码
    """
    # 先尝试学生登录
    student = auth.authenticate_student(db, form_data.username, form_data.password)
    if student:
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": student.student_id, "user_type": "student"},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "student",
            "user_id": student.student_id
        }
    
    # 再尝试管理员登录
    admin = auth.authenticate_admin(db, form_data.username, form_data.password)
    if admin:
        # 更新最后登录时间
        admin.last_login = datetime.utcnow()
        db.commit()
        
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": admin.username, "user_type": "admin"},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "admin",
            "user_id": str(admin.admin_id)
        }
    
    # 登录失败
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或密码错误",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的信息
    """
    user, user_type = current_user
    
    if user_type == "student":
        return {
            "user_type": "student",
            "student_id": user.student_id,
            "name": user.name,
            "email": user.email,
            "college": user.college,
            "dorm_id": user.dorm_id
        }
    else:
        return {
            "user_type": "admin",
            "admin_id": user.admin_id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }


@router.post("/logout", response_model=schemas.MessageResponse, summary="用户登出")
async def logout():
    """
    用户登出（前端删除Token即可）
    """
    return {"message": "登出成功"}
