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


@router.post("/register", response_model=schemas.Token, summary="学生注册")
async def register(
    student_data: schemas.StudentRegister,
    db: Session = Depends(get_db)
):
    """
    新学生注册账户
    
    - **student_id**: 学号(9位)
    - **password**: 密码(至少6位)
    - **name**: 姓名
    - **gender**: 性别(男/女)
    - **nationality**: 国籍
    - **college**: 学院代码(SSE/SME/MED/HSS/SAI/SDS/MUS)
    - **enrollment_year**: 入学年份
    - **email**: 邮箱
    """




    
    # 检查学号是否已存在
    existing_student = db.query(models.Student).filter(
        models.Student.student_id == student_data.student_id
    ).first()
    
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该学号已被注册"
        )
    
    # 检查邮箱是否已存在
    existing_email = db.query(models.Student).filter(
        models.Student.email == student_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被使用"
        )
    
    # 验证性别
    if student_data.gender not in ["男", "女"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="性别必须是'男'或'女'"
        )
    
    # 验证学院代码
    valid_colleges = ["SSE", "SME", "MED", "HSS", "SAI", "SDS", "MUS"]
    if student_data.college not in valid_colleges:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"学院代码必须是以下之一: {', '.join(valid_colleges)}"
        )
    
    # 查找有空床位的同性别宿舍
    available_dorm = db.query(models.Dormitory).filter(
        models.Dormitory.gender_type == student_data.gender,
        models.Dormitory.occupied_beds < models.Dormitory.total_beds
    ).order_by(models.Dormitory.dorm_id).first()
    
    if not available_dorm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"抱歉,当前没有可用的{student_data.gender}生宿舍,请联系管理员"
        )
    
    # 创建新学生并分配宿舍
    hashed_password = auth.get_password_hash(student_data.password)
    new_student = models.Student(
        student_id=student_data.student_id,
        password=hashed_password,
        name=student_data.name,
        gender=student_data.gender,
        nationality=student_data.nationality,
        college=student_data.college,
        enrollment_year=student_data.enrollment_year,
        email=student_data.email,
        dorm_id=available_dorm.dorm_id  # 自动分配宿舍
    )
    
    # 更新宿舍占用床位数
    available_dorm.occupied_beds += 1
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    # 自动登录，生成Token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": new_student.student_id, "user_type": "student"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "student",
        "user_id": new_student.student_id
    }


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
