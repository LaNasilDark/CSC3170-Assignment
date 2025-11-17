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
