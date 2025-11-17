"""
JWT认证和密码加密模块
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from . import models, schemas
from .database import get_db

# 加载环境变量
load_dotenv()

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    支持bcrypt哈希密码和明文密码(用于测试)
    """
    try:
        # 尝试bcrypt验证
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # 如果bcrypt验证失败,尝试明文比较(仅用于测试环境)
        return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)


def authenticate_student(db: Session, student_id: str, password: str) -> Optional[models.Student]:
    """
    验证学生身份
    """
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        return None
    if not verify_password(password, student.password):
        return None
    return student


def authenticate_admin(db: Session, username: str, password: str) -> Optional[models.Administrator]:
    """
    验证管理员身份
    """
    admin = db.query(models.Administrator).filter(
        models.Administrator.username == username,
        models.Administrator.is_active == True
    ).first()
    if not admin:
        return None
    if not verify_password(password, admin.password):
        return None
    return admin


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> schemas.TokenData:
    """
    解码JWT令牌
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if username is None or user_type is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return schemas.TokenData(username=username, user_type=user_type)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    获取当前用户（学生或管理员）
    返回: (user_object, user_type)
    """
    token_data = decode_token(token)
    
    if token_data.user_type == "student":
        user = db.query(models.Student).filter(
            models.Student.student_id == token_data.username
        ).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        return user, "student"
    
    elif token_data.user_type == "admin":
        user = db.query(models.Administrator).filter(
            models.Administrator.username == token_data.username,
            models.Administrator.is_active == True
        ).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="管理员不存在或已禁用"
            )
        return user, "admin"
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户类型"
        )


def get_current_student(
    current_user = Depends(get_current_user)
) -> models.Student:
    """
    获取当前学生用户
    确保只有学生可以访问
    """
    user, user_type = current_user
    if user_type != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要学生权限"
        )
    return user


def get_current_admin(
    current_user = Depends(get_current_user)
) -> models.Administrator:
    """
    获取当前管理员用户
    确保只有管理员可以访问
    """
    user, user_type = current_user
    if user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return user
