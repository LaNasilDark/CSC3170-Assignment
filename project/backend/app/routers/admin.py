"""
管理员功能API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime

from .. import schemas, auth, models
from ..database import get_db

router = APIRouter(prefix="/api/admin", tags=["管理员功能"])


# ============================================================================
# 宿舍管理
# ============================================================================

@router.get("/dormitories", summary="查看所有宿舍")
async def get_all_dormitories(
    building: Optional[str] = Query(None, description="按楼栋筛选"),
    gender_type: Optional[str] = Query(None, description="按性别筛选"),
    has_vacancy: Optional[bool] = Query(None, description="仅显示有空位的宿舍"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查看所有宿舍信息,支持筛选和分页
    """
    query = db.query(models.Dormitory)
    
    # 应用筛选条件
    if building:
        query = query.filter(models.Dormitory.building_no == building)
    if gender_type:
        query = query.filter(models.Dormitory.gender_type == gender_type)
    if has_vacancy is True:
        query = query.filter(models.Dormitory.occupied_beds < models.Dormitory.total_beds)
    
    total = query.count()
    dormitories = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": dormitories,
        "skip": skip,
        "limit": limit
    }


@router.get("/dormitories/{dorm_id}", summary="查看宿舍详情")
async def get_dormitory_detail(
    dorm_id: int,
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查看特定宿舍的详细信息,包括居住学生列表
    """
    dormitory = db.query(models.Dormitory).filter(
        models.Dormitory.dorm_id == dorm_id
    ).first()
    
    if not dormitory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="宿舍不存在"
        )
    
    # 获取该宿舍的所有学生
    students = db.query(models.Student).filter(
        models.Student.dorm_id == dorm_id
    ).all()
    
    return {
        "dormitory": dormitory,
        "students": students,
        "vacancy": dormitory.total_beds - dormitory.occupied_beds
    }


# ============================================================================
# 学生管理
# ============================================================================

@router.get("/students", summary="查看所有学生")
async def get_all_students(
    search: Optional[str] = Query(None, description="搜索学号或姓名"),
    college: Optional[str] = Query(None, description="按学院筛选"),
    gender: Optional[str] = Query(None, description="按性别筛选"),
    enrollment_year: Optional[int] = Query(None, description="按入学年份筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查看所有学生信息,支持搜索、筛选和分页
    """
    query = db.query(models.Student)
    
    # 搜索功能
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Student.student_id.like(search_pattern),
                models.Student.name.like(search_pattern)
            )
        )
    
    # 应用筛选条件
    if college:
        query = query.filter(models.Student.college == college)
    if gender:
        query = query.filter(models.Student.gender == gender)
    if enrollment_year:
        query = query.filter(models.Student.enrollment_year == enrollment_year)
    
    total = query.count()
    students = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": students,
        "skip": skip,
        "limit": limit
    }


@router.get("/students/{student_id}", summary="查看学生详情")
async def get_student_detail(
    student_id: str,
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查看特定学生的详细信息
    """
    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )
    
    # 获取学生的宿舍信息
    dormitory = None
    if student.dorm_id:
        dormitory = db.query(models.Dormitory).filter(
            models.Dormitory.dorm_id == student.dorm_id
        ).first()
    
    return {
        "student": student,
        "dormitory": dormitory
    }


@router.put("/students/{student_id}", summary="更新学生信息")
async def update_student_info(
    student_id: str,
    student_update: schemas.AdminStudentUpdate,
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员更新学生信息
    可以修改姓名、性别、国籍、学院、入学年份、邮箱、宿舍分配
    """
    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )
    
    # 获取要更新的字段
    update_data = student_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供一个要更新的字段"
        )
    
    # 如果修改邮箱,检查唯一性
    if "email" in update_data and update_data["email"] != student.email:
        existing = db.query(models.Student).filter(
            models.Student.email == update_data["email"],
            models.Student.student_id != student_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他学生使用"
            )
    
    # 如果修改宿舍
    if "dorm_id" in update_data:
        new_dorm_id = update_data["dorm_id"]
        old_dorm_id = student.dorm_id
        
        # 如果是分配新宿舍(不是清除宿舍)
        if new_dorm_id is not None:
            new_dorm = db.query(models.Dormitory).filter(
                models.Dormitory.dorm_id == new_dorm_id
            ).first()
            
            if not new_dorm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="目标宿舍不存在"
                )
            
            # 检查性别是否匹配
            student_gender = update_data.get("gender", student.gender)
            if new_dorm.gender_type != student_gender:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"目标宿舍性别类型({new_dorm.gender_type})与学生性别({student_gender})不匹配"
                )
            
            # 检查是否有空位(如果不是原宿舍)
            if new_dorm_id != old_dorm_id and new_dorm.occupied_beds >= new_dorm.total_beds:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="目标宿舍已满"
                )
        
        # 更新床位计数
        if old_dorm_id != new_dorm_id:
            # 减少原宿舍床位
            if old_dorm_id:
                old_dorm = db.query(models.Dormitory).filter(
                    models.Dormitory.dorm_id == old_dorm_id
                ).first()
                if old_dorm and old_dorm.occupied_beds > 0:
                    old_dorm.occupied_beds -= 1
            
            # 增加新宿舍床位
            if new_dorm_id:
                new_dorm = db.query(models.Dormitory).filter(
                    models.Dormitory.dorm_id == new_dorm_id
                ).first()
                if new_dorm:
                    new_dorm.occupied_beds += 1
    
    # 应用更新
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    
    return student


# ============================================================================
# 宿舍调换申请管理
# ============================================================================

@router.get("/dorm-change-requests", summary="查看所有调换申请")
async def get_dorm_change_requests(
    status_filter: Optional[str] = Query(None, description="按状态筛选: pending/approved/rejected"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查看所有宿舍调换申请
    """
    query = db.query(models.DormChangeRequest)
    
    if status_filter:
        query = query.filter(models.DormChangeRequest.status == status_filter)
    
    total = query.count()
    requests = query.order_by(
        models.DormChangeRequest.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": requests,
        "skip": skip,
        "limit": limit
    }


@router.put("/dorm-change-requests/{request_id}", summary="处理调换申请")
async def process_dorm_change_request(
    request_id: int,
    action: str = Query(..., description="操作: approve/reject"),
    admin_comment: Optional[str] = Query(None, max_length=500, description="管理员备注"),
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    审批或拒绝宿舍调换申请
    """
    if action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="操作必须是'approve'或'reject'"
        )
    
    request = db.query(models.DormChangeRequest).filter(
        models.DormChangeRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="申请不存在"
        )
    
    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该申请当前状态为'{request.status}',无法处理"
        )
    
    # 更新申请状态
    request.status = "approved" if action == "approve" else "rejected"
    request.admin_id = current_admin.admin_id
    request.admin_comment = admin_comment
    request.processed_at = datetime.utcnow()
    
    # 如果批准,需要更新学生宿舍并调整床位数
    if action == "approve":
        student = db.query(models.Student).filter(
            models.Student.student_id == request.student_id
        ).first()
        
        if student and student.dorm_id:
            # 减少原宿舍的occupied_beds
            old_dorm = db.query(models.Dormitory).filter(
                models.Dormitory.dorm_id == student.dorm_id
            ).first()
            if old_dorm and old_dorm.occupied_beds > 0:
                old_dorm.occupied_beds -= 1
        
        # 增加新宿舍的occupied_beds
        new_dorm = db.query(models.Dormitory).filter(
            models.Dormitory.dorm_id == request.target_dorm_id
        ).first()
        
        if not new_dorm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="目标宿舍不存在"
            )
        
        if new_dorm.occupied_beds >= new_dorm.total_beds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="目标宿舍已满,无法批准"
            )
        
        new_dorm.occupied_beds += 1
        
        # 更新学生宿舍
        if student:
            student.dorm_id = request.target_dorm_id
    
    db.commit()
    db.refresh(request)
    
    return request


# ============================================================================
# 维修申请管理
# ============================================================================

@router.get("/maintenance-requests", summary="查看所有维修申请")
async def get_maintenance_requests(
    status_filter: Optional[str] = Query(None, description="按状态筛选: pending/in_progress/completed/cancelled"),
    priority: Optional[str] = Query(None, description="按优先级筛选: low/medium/high/urgent"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查看所有维修申请
    """
    query = db.query(models.MaintenanceRequest)
    
    if status_filter:
        query = query.filter(models.MaintenanceRequest.status == status_filter)
    if priority:
        query = query.filter(models.MaintenanceRequest.priority == priority)
    
    total = query.count()
    requests = query.order_by(
        models.MaintenanceRequest.priority.desc(),
        models.MaintenanceRequest.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": requests,
        "skip": skip,
        "limit": limit
    }


@router.put("/maintenance-requests/{request_id}", summary="更新维修申请")
async def update_maintenance_request(
    request_id: int,
    update_data: schemas.MaintenanceRequestUpdate,
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新维修申请状态和评论
    """
    request = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修申请不存在"
        )
    
    # 更新字段
    if update_data.status:
        request.status = update_data.status
        if update_data.status == "completed":
            request.completed_at = datetime.utcnow()
    
    if update_data.admin_comment is not None:
        request.admin_comment = update_data.admin_comment
    
    request.admin_id = current_admin.admin_id
    
    db.commit()
    db.refresh(request)
    
    return request


# ============================================================================
# 账单管理
# ============================================================================

@router.get("/bills", summary="查看所有账单")
async def get_all_bills(
    status_filter: Optional[str] = Query(None, description="按状态筛选: unpaid/paid/overdue"),
    bill_type: Optional[str] = Query(None, description="按类型筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查看所有账单
    """
    query = db.query(models.Bill)
    
    if status_filter:
        query = query.filter(models.Bill.status == status_filter)
    if bill_type:
        query = query.filter(models.Bill.bill_type == bill_type)
    
    total = query.count()
    bills = query.order_by(
        models.Bill.due_date.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": bills,
        "skip": skip,
        "limit": limit
    }


@router.put("/bills/{bill_id}", summary="更新账单状态")
async def update_bill_status(
    bill_id: int,
    new_status: str = Query(..., description="新状态: unpaid/paid/overdue"),
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新账单状态
    """
    if new_status not in ["unpaid", "paid", "overdue"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="状态必须是'unpaid'、'paid'或'overdue'"
        )
    
    bill = db.query(models.Bill).filter(models.Bill.bill_id == bill_id).first()
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账单不存在"
        )
    
    bill.status = new_status
    if new_status == "paid":
        bill.payment_date = datetime.utcnow()
    
    db.commit()
    db.refresh(bill)
    
    return bill


# ============================================================================
# 统计数据
# ============================================================================

@router.get("/statistics", summary="查看系统统计数据")
async def get_statistics(
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取系统整体统计数据
    """
    # 学生统计
    total_students = db.query(func.count(models.Student.student_id)).scalar()
    students_with_dorm = db.query(func.count(models.Student.student_id)).filter(
        models.Student.dorm_id.isnot(None)
    ).scalar()
    
    # 宿舍统计
    total_dorms = db.query(func.count(models.Dormitory.dorm_id)).scalar()
    total_beds = db.query(func.sum(models.Dormitory.total_beds)).scalar() or 0
    occupied_beds = db.query(func.sum(models.Dormitory.occupied_beds)).scalar() or 0
    
    # 申请统计
    pending_dorm_changes = db.query(func.count(models.DormChangeRequest.request_id)).filter(
        models.DormChangeRequest.status == "pending"
    ).scalar()
    
    pending_maintenance = db.query(func.count(models.MaintenanceRequest.request_id)).filter(
        models.MaintenanceRequest.status == "pending"
    ).scalar()
    
    # 账单统计
    unpaid_bills = db.query(func.count(models.Bill.bill_id)).filter(
        models.Bill.status == "unpaid"
    ).scalar()
    
    total_unpaid_amount = db.query(func.sum(models.Bill.amount)).filter(
        models.Bill.status == "unpaid"
    ).scalar() or 0
    
    return {
        "students": {
            "total": total_students,
            "with_dorm": students_with_dorm,
            "without_dorm": total_students - students_with_dorm
        },
        "dormitories": {
            "total": total_dorms,
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "vacant_beds": total_beds - occupied_beds,
            "occupancy_rate": round(occupied_beds / total_beds * 100, 2) if total_beds > 0 else 0
        },
        "requests": {
            "pending_dorm_changes": pending_dorm_changes,
            "pending_maintenance": pending_maintenance
        },
        "bills": {
            "unpaid_count": unpaid_bills,
            "unpaid_amount": float(total_unpaid_amount)
        }
    }


# ============================================================================
# 管理员自我管理
# ============================================================================

@router.put("/profile", summary="管理员更新自己的信息")
def update_admin_profile(
    profile_update: schemas.AdminProfileUpdate,
    current_admin: models.Administrator = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员更新自己的账户信息
    
    可更新字段:
    - name: 姓名
    - email: 邮箱(需唯一)
    - phone: 电话
    - password: 密码(需提供old_password验证)
    
    安全限制:
    - 不能修改username
    - 不能修改role
    - 不能修改is_active
    - 修改密码需验证旧密码
    """
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    
    ph = PasswordHasher(
        memory_cost=65536,
        time_cost=3,
        parallelism=4
    )
    
    # 获取当前管理员信息
    admin = db.query(models.Administrator).filter(
        models.Administrator.username == current_admin.username
    ).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")
    
    # 准备更新数据
    update_data = {}
    
    # 更新姓名
    if profile_update.name is not None:
        update_data["name"] = profile_update.name
    
    # 更新邮箱(检查唯一性)
    if profile_update.email is not None:
        existing = db.query(models.Administrator).filter(
            models.Administrator.email == profile_update.email,
            models.Administrator.admin_id != admin.admin_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="邮箱已被其他管理员使用")
        update_data["email"] = profile_update.email
    
    # 更新电话
    if profile_update.phone is not None:
        update_data["phone"] = profile_update.phone
    
    # 更新密码(需验证旧密码)
    if profile_update.new_password is not None:
        if not profile_update.old_password:
            raise HTTPException(status_code=400, detail="修改密码时必须提供旧密码")
        
        # 验证旧密码
        try:
            ph.verify(admin.password, profile_update.old_password)
        except VerifyMismatchError:
            raise HTTPException(status_code=400, detail="旧密码错误")
        
        # 哈希新密码
        hashed_password = ph.hash(profile_update.new_password)
        update_data["password"] = hashed_password
    
    # 如果没有任何更新
    if not update_data:
        raise HTTPException(status_code=400, detail="未提供任何更新字段")
    
    # 执行更新
    for key, value in update_data.items():
        setattr(admin, key, value)
    
    db.commit()
    db.refresh(admin)
    
    return {
        "message": "管理员信息更新成功",
        "admin_id": admin.admin_id,
        "username": admin.username,
        "updated_fields": list(update_data.keys())
    }
