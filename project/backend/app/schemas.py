"""
Pydantic数据模型定义
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# 认证相关
# ============================================================================

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名/学号")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """JWT Token响应"""
    access_token: str
    token_type: str = "bearer"
    user_type: str  # "student" or "admin"
    user_id: str


class TokenData(BaseModel):
    """Token数据"""
    username: Optional[str] = None
    user_type: Optional[str] = None


# ============================================================================
# 学生相关
# ============================================================================

class StudentBase(BaseModel):
    """学生基础信息"""
    name: str
    gender: str
    nationality: str
    college: str
    enrollment_year: int
    email: EmailStr


class StudentRegister(BaseModel):
    """学生注册"""
    student_id: str = Field(..., min_length=9, max_length=9, description="学号(9位)")
    password: str = Field(..., min_length=6, description="密码(至少6位)")
    name: str = Field(..., min_length=2, description="姓名")
    gender: str = Field(..., description="性别: 男/女")
    nationality: str = Field(..., description="国籍")
    college: str = Field(..., description="学院代码: SSE/SME/MED/HSS/SAI/SDS/MUS")
    enrollment_year: int = Field(..., ge=2020, le=2030, description="入学年份")
    email: EmailStr = Field(..., description="邮箱")


class StudentProfile(StudentBase):
    """学生个人信息"""
    student_id: str
    dorm_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StudentUpdate(BaseModel):
    """学生信息更新"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """密码修改"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


# ============================================================================
# 宿舍相关
# ============================================================================

class DormitoryBase(BaseModel):
    """宿舍基础信息"""
    building_no: str
    floor_no: int
    room_no: str
    gender_type: str
    total_beds: int
    occupied_beds: int


class DormitoryInfo(DormitoryBase):
    """宿舍详细信息"""
    dorm_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoommateInfo(BaseModel):
    """室友信息"""
    student_id: str
    name: str
    gender: str
    college: str
    enrollment_year: int

    class Config:
        from_attributes = True


# ============================================================================
# 宿舍调换申请相关
# ============================================================================

class DormChangeRequestCreate(BaseModel):
    """创建宿舍调换申请"""
    target_dorm_id: int = Field(..., description="目标宿舍ID")
    reason: str = Field(..., min_length=5, max_length=500, description="申请理由")


class DormChangeRequestInfo(BaseModel):
    """宿舍调换申请信息"""
    request_id: int
    student_id: str
    current_dorm_id: int
    target_dorm_id: int
    reason: Optional[str] = None
    status: str
    admin_id: Optional[int] = None
    admin_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DormChangeRequestWithDetails(DormChangeRequestInfo):
    """宿舍调换申请详细信息（包含宿舍和学生信息）"""
    student_name: Optional[str] = None
    current_room_no: Optional[str] = None
    target_room_no: Optional[str] = None


class DormChangeRequestResponse(BaseModel):
    """审批宿舍调换申请"""
    admin_comment: Optional[str] = Field(None, max_length=500)


# ============================================================================
# 维修申请相关
# ============================================================================

class MaintenanceRequestCreate(BaseModel):
    """创建维修申请"""
    issue_type: str = Field(..., description="问题类型: 水电/家具/网络/其他")
    description: str = Field(..., min_length=1, max_length=500, description="问题描述")
    priority: Optional[str] = Field("medium", description="优先级: low/medium/high/urgent")


class MaintenanceRequestInfo(BaseModel):
    """维修申请信息"""
    request_id: int
    student_id: str
    dorm_id: int
    issue_type: str
    description: str
    status: str
    priority: str
    admin_id: Optional[int] = None
    admin_comment: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaintenanceRequestWithDetails(MaintenanceRequestInfo):
    """维修申请详细信息"""
    student_name: Optional[str] = None
    room_no: Optional[str] = None


class MaintenanceRequestUpdate(BaseModel):
    """更新维修申请(管理员用)"""
    status: Optional[str] = None
    admin_comment: Optional[str] = Field(None, max_length=500)


class MaintenanceRequestStudentUpdate(BaseModel):
    """学生更新维修申请"""
    issue_type: Optional[str] = Field(None, description="问题类型: 水电/家具/网络/其他")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="问题描述")
    priority: Optional[str] = Field(None, description="优先级: low/medium/high/urgent")


# ============================================================================
# 账单相关
# ============================================================================

class BillInfo(BaseModel):
    """账单信息"""
    bill_id: int
    dorm_id: int
    bill_type: str
    amount: Decimal
    billing_month: str
    due_date: date
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BillWithDormInfo(BillInfo):
    """账单信息（包含宿舍信息）"""
    room_no: Optional[str] = None


# ============================================================================
# 管理员相关
# ============================================================================

class AdminBase(BaseModel):
    """管理员基础信息"""
    username: str
    name: str
    email: EmailStr
    role: str
    phone: Optional[str] = None


class AdminInfo(AdminBase):
    """管理员信息"""
    admin_id: int
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# 通用响应
# ============================================================================

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    data: List


class StatisticsResponse(BaseModel):
    """统计数据响应"""
    total_students: int
    total_dormitories: int
    occupied_dormitories: int
    pending_dorm_changes: int
    pending_maintenance: int
