"""
学生功能API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, auth, models
from ..database import get_db

router = APIRouter(prefix="/api/students", tags=["学生功能"])


@router.get("/profile", response_model=schemas.StudentProfile, summary="查看个人信息")
async def get_student_profile(
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    查看学生个人信息
    """
    return current_student


@router.get("/dormitory", summary="查看宿舍信息")
async def get_student_dormitory(
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    查看学生当前宿舍信息
    """
    if not current_student.dorm_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="您尚未分配宿舍"
        )
    
    dormitory = db.query(models.Dormitory).filter(
        models.Dormitory.dorm_id == current_student.dorm_id
    ).first()
    
    if not dormitory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="宿舍信息不存在"
        )
    
    return {
        "dorm_id": dormitory.dorm_id,
        "building_no": dormitory.building_no,
        "floor_no": dormitory.floor_no,
        "room_no": dormitory.room_no,
        "gender_type": dormitory.gender_type,
        "total_beds": dormitory.total_beds,
        "occupied_beds": dormitory.occupied_beds,
        "available_beds": dormitory.total_beds - dormitory.occupied_beds
    }


@router.get("/roommates", response_model=List[schemas.RoommateInfo], summary="查看室友")
async def get_roommates(
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    查看当前宿舍的室友信息
    """
    if not current_student.dorm_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="您尚未分配宿舍"
        )
    
    # 查询同宿舍的其他学生
    roommates = db.query(models.Student).filter(
        models.Student.dorm_id == current_student.dorm_id,
        models.Student.student_id != current_student.student_id
    ).all()
    
    return roommates


@router.get("/dormitories", summary="查询宿舍列表")
async def query_dormitories(
    building_no: str = None,
    room_no: str = None,
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    查询宿舍列表（用于宿舍调换申请时验证目标宿舍）
    """
    query = db.query(models.Dormitory)
    
    if building_no:
        query = query.filter(models.Dormitory.building_no == building_no)
    if room_no:
        query = query.filter(models.Dormitory.room_no == room_no)
    
    dormitories = query.all()
    
    result = []
    for dorm in dormitories:
        result.append({
            "dorm_id": dorm.dorm_id,
            "building_no": dorm.building_no,
            "room_no": dorm.room_no,
            "gender_type": dorm.gender_type,
            "total_beds": dorm.total_beds,
            "occupied_beds": dorm.occupied_beds
        })
    
    return result


@router.get("/bills", response_model=List[schemas.BillWithDormInfo], summary="查看账单")
async def get_student_bills(
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    查看学生宿舍的账单信息
    """
    if not current_student.dorm_id:
        return []
    
    # 查询宿舍账单
    bills = db.query(
        models.Bill,
        models.Dormitory.room_no
    ).join(
        models.Dormitory,
        models.Bill.dorm_id == models.Dormitory.dorm_id
    ).filter(
        models.Bill.dorm_id == current_student.dorm_id
    ).order_by(
        models.Bill.billing_month.desc()
    ).all()
    
    result = []
    for bill, room_no in bills:
        bill_dict = {
            "bill_id": bill.bill_id,
            "dorm_id": bill.dorm_id,
            "bill_type": bill.bill_type,
            "amount": bill.amount,
            "billing_month": bill.billing_month,
            "due_date": bill.due_date,
            "status": bill.status,
            "paid_at": bill.paid_at,
            "created_at": bill.created_at,
            "room_no": room_no
        }
        result.append(bill_dict)
    
    return result


@router.post(
    "/dorm-change",
    response_model=schemas.DormChangeRequestInfo,
    status_code=status.HTTP_201_CREATED,
    summary="提交宿舍调换申请"
)
async def create_dorm_change_request(
    request_data: schemas.DormChangeRequestCreate,
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    提交宿舍调换申请
    """
    if not current_student.dorm_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您尚未分配宿舍，无法申请调换"
        )
    
    # 检查目标宿舍是否存在
    target_dorm = db.query(models.Dormitory).filter(
        models.Dormitory.dorm_id == request_data.target_dorm_id
    ).first()
    
    if not target_dorm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标宿舍不存在"
        )
    
    # 检查性别是否匹配
    if target_dorm.gender_type != current_student.gender:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目标宿舍性别不匹配"
        )
    
    # 检查是否有空床位
    if target_dorm.occupied_beds >= target_dorm.total_beds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目标宿舍已满"
        )
    
    # 检查是否有待处理的申请
    existing_request = db.query(models.DormChangeRequest).filter(
        models.DormChangeRequest.student_id == current_student.student_id,
        models.DormChangeRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已有待处理的宿舍调换申请"
        )
    
    # 创建申请
    new_request = models.DormChangeRequest(
        student_id=current_student.student_id,
        current_dorm_id=current_student.dorm_id,
        target_dorm_id=request_data.target_dorm_id,
        reason=request_data.reason,
        status="pending"
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return new_request


@router.get("/dorm-change", response_model=List[schemas.DormChangeRequestInfo], summary="查看宿舍调换申请")
async def get_dorm_change_requests(
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    查看自己的宿舍调换申请记录
    """
    requests = db.query(models.DormChangeRequest).filter(
        models.DormChangeRequest.student_id == current_student.student_id
    ).order_by(
        models.DormChangeRequest.created_at.desc()
    ).all()
    
    return requests


@router.post(
    "/maintenance",
    response_model=schemas.MaintenanceRequestInfo,
    status_code=status.HTTP_201_CREATED,
    summary="提交维修申请"
)
async def create_maintenance_request(
    request_data: schemas.MaintenanceRequestCreate,
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    提交维修申请
    """
    if not current_student.dorm_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您尚未分配宿舍，无法提交维修申请"
        )
    
    # 创建维修申请
    new_request = models.MaintenanceRequest(
        student_id=current_student.student_id,
        dorm_id=current_student.dorm_id,
        issue_type=request_data.issue_type,
        description=request_data.description,
        priority=request_data.priority or "medium",
        status="pending"
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return new_request


@router.get("/maintenance", response_model=List[schemas.MaintenanceRequestInfo], summary="查看维修申请")
async def get_maintenance_requests(
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    查看自己的维修申请记录
    """
    requests = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.student_id == current_student.student_id
    ).order_by(
        models.MaintenanceRequest.created_at.desc()
    ).all()
    
    return requests


@router.put(
    "/maintenance/{request_id}",
    response_model=schemas.MaintenanceRequestInfo,
    summary="修改维修申请"
)
async def update_maintenance_request(
    request_id: int,
    request_update: schemas.MaintenanceRequestStudentUpdate,
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    修改已提交但未完成的维修申请
    只能修改状态为pending(待处理)或in_progress(处理中)的申请
    """
    # 查找维修申请
    maintenance_request = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.request_id == request_id,
        models.MaintenanceRequest.student_id == current_student.student_id
    ).first()
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修申请不存在或您无权修改"
        )
    
    # 检查申请状态,只允许修改未完成的申请
    if maintenance_request.status not in ["pending", "in_progress"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"当前状态为'{maintenance_request.status}',无法修改。只能修改状态为'pending'或'in_progress'的申请"
        )
    
    # 更新字段
    update_data = request_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供一个要更新的字段"
        )
    
    for field, value in update_data.items():
        setattr(maintenance_request, field, value)
    
    db.commit()
    db.refresh(maintenance_request)
    
    return maintenance_request


@router.put("/profile", response_model=schemas.StudentProfile, summary="修改个人信息")
async def update_student_profile(
    student_update: schemas.StudentUpdate,
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    修改学生个人信息（姓名和邮箱）
    
    注意：只能修改姓名和邮箱，其他字段（如性别、国籍、学院等）不可修改
    """
    # 更新姓名
    if student_update.name is not None:
        if len(student_update.name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="姓名至少需要2个字符"
            )
        current_student.name = student_update.name.strip()
    
    # 更新邮箱
    if student_update.email is not None:
        # 检查邮箱是否已被其他学生使用
        existing_student = db.query(models.Student).filter(
            models.Student.email == student_update.email,
            models.Student.student_id != current_student.student_id
        ).first()
        
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他学生使用"
            )
        
        current_student.email = student_update.email
    
    db.commit()
    db.refresh(current_student)
    
    return current_student


@router.put("/password", response_model=schemas.MessageResponse, summary="修改密码")
async def change_password(
    password_data: schemas.PasswordChange,
    current_student: models.Student = Depends(auth.get_current_student),
    db: Session = Depends(get_db)
):
    """
    修改学生密码
    """
    # 验证旧密码
    if not auth.verify_password(password_data.old_password, current_student.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    current_student.password = auth.get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}
