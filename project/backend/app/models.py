"""
SQLAlchemy ORM模型定义
对应数据库中的6张表
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime, Text, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class GenderEnum(str, enum.Enum):
    """性别枚举"""
    MALE = "男"
    FEMALE = "女"


class RequestStatusEnum(str, enum.Enum):
    """申请状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MaintenanceStatusEnum(str, enum.Enum):
    """维修状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriorityEnum(str, enum.Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BillStatusEnum(str, enum.Enum):
    """账单状态枚举"""
    UNPAID = "unpaid"
    PAID = "paid"
    OVERDUE = "overdue"


class AdminRoleEnum(str, enum.Enum):
    """管理员角色枚举"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MAINTENANCE_STAFF = "maintenance_staff"


class Student(Base):
    """学生表"""
    __tablename__ = "students"

    student_id = Column(String(20), primary_key=True, comment="学号")
    password = Column(String(255), nullable=False, comment="密码")
    name = Column(String(100), nullable=False, comment="姓名")
    gender = Column(String(10), nullable=False, comment="性别")
    nationality = Column(String(50), nullable=False, comment="国籍")
    college = Column(String(50), nullable=False, comment="学院代码")
    enrollment_year = Column(Integer, nullable=False, comment="入学年份")
    email = Column(String(100), nullable=False, unique=True, comment="邮箱")
    dorm_id = Column(Integer, ForeignKey("dormitories.dorm_id", ondelete="SET NULL"), comment="宿舍ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    dormitory = relationship("Dormitory", back_populates="students")
    dorm_change_requests = relationship("DormChangeRequest", back_populates="student")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="student")


class Dormitory(Base):
    """宿舍表"""
    __tablename__ = "dormitories"

    dorm_id = Column(Integer, primary_key=True, autoincrement=True, comment="宿舍ID")
    building_no = Column(String(10), nullable=False, comment="楼栋号")
    floor_no = Column(Integer, nullable=False, comment="楼层号")
    room_no = Column(String(20), nullable=False, unique=True, comment="房间号")
    gender_type = Column(String(10), nullable=False, comment="性别类型")
    total_beds = Column(Integer, nullable=False, default=4, comment="总床位数")
    occupied_beds = Column(Integer, nullable=False, default=0, comment="已占用床位数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    students = relationship("Student", back_populates="dormitory")
    dorm_change_requests_current = relationship(
        "DormChangeRequest",
        foreign_keys="DormChangeRequest.current_dorm_id",
        back_populates="current_dormitory"
    )
    dorm_change_requests_target = relationship(
        "DormChangeRequest",
        foreign_keys="DormChangeRequest.target_dorm_id",
        back_populates="target_dormitory"
    )
    maintenance_requests = relationship("MaintenanceRequest", back_populates="dormitory")
    bills = relationship("Bill", back_populates="dormitory")


class DormChangeRequest(Base):
    """宿舍调换申请表"""
    __tablename__ = "dorm_change_requests"

    request_id = Column(Integer, primary_key=True, autoincrement=True, comment="申请ID")
    student_id = Column(String(20), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, comment="申请学生ID")
    current_dorm_id = Column(Integer, ForeignKey("dormitories.dorm_id", ondelete="CASCADE"), nullable=False, comment="当前宿舍ID")
    target_dorm_id = Column(Integer, ForeignKey("dormitories.dorm_id", ondelete="CASCADE"), nullable=False, comment="目标宿舍ID")
    reason = Column(Text, comment="申请理由")
    status = Column(Enum(RequestStatusEnum), nullable=False, default=RequestStatusEnum.PENDING, comment="申请状态")
    admin_id = Column(Integer, ForeignKey("administrators.admin_id", ondelete="SET NULL"), comment="处理管理员ID")
    admin_comment = Column(Text, comment="管理员备注")
    created_at = Column(DateTime, server_default=func.now(), comment="申请时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    student = relationship("Student", back_populates="dorm_change_requests")
    current_dormitory = relationship("Dormitory", foreign_keys=[current_dorm_id], back_populates="dorm_change_requests_current")
    target_dormitory = relationship("Dormitory", foreign_keys=[target_dorm_id], back_populates="dorm_change_requests_target")
    admin = relationship("Administrator", back_populates="dorm_change_requests")


class MaintenanceRequest(Base):
    """维修申请表"""
    __tablename__ = "maintenance_requests"

    request_id = Column(Integer, primary_key=True, autoincrement=True, comment="申请ID")
    student_id = Column(String(20), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, comment="申请学生ID")
    dorm_id = Column(Integer, ForeignKey("dormitories.dorm_id", ondelete="CASCADE"), nullable=False, comment="宿舍ID")
    issue_type = Column(String(50), nullable=False, comment="问题类型")
    description = Column(Text, nullable=False, comment="问题描述")
    status = Column(Enum(MaintenanceStatusEnum), nullable=False, default=MaintenanceStatusEnum.PENDING, comment="处理状态")
    priority = Column(Enum(PriorityEnum), nullable=False, default=PriorityEnum.MEDIUM, comment="优先级")
    admin_id = Column(Integer, ForeignKey("administrators.admin_id", ondelete="SET NULL"), comment="处理管理员ID")
    admin_comment = Column(Text, comment="处理备注")
    completed_at = Column(DateTime, comment="完成时间")
    created_at = Column(DateTime, server_default=func.now(), comment="申请时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    student = relationship("Student", back_populates="maintenance_requests")
    dormitory = relationship("Dormitory", back_populates="maintenance_requests")
    admin = relationship("Administrator", back_populates="maintenance_requests")


class Bill(Base):
    """账单表"""
    __tablename__ = "bills"

    bill_id = Column(Integer, primary_key=True, autoincrement=True, comment="账单ID")
    dorm_id = Column(Integer, ForeignKey("dormitories.dorm_id", ondelete="CASCADE"), nullable=False, comment="宿舍ID")
    bill_type = Column(String(50), nullable=False, comment="账单类型")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="金额")
    billing_month = Column(String(7), nullable=False, comment="账单月份")
    due_date = Column(Date, nullable=False, comment="截止日期")
    status = Column(Enum(BillStatusEnum), nullable=False, default=BillStatusEnum.UNPAID, comment="支付状态")
    paid_at = Column(DateTime, comment="支付时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    dormitory = relationship("Dormitory", back_populates="bills")


class Administrator(Base):
    """管理员表"""
    __tablename__ = "administrators"

    admin_id = Column(Integer, primary_key=True, autoincrement=True, comment="管理员ID")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    name = Column(String(100), nullable=False, comment="姓名")
    email = Column(String(100), nullable=False, unique=True, comment="邮箱")
    role = Column(Enum(AdminRoleEnum), nullable=False, default=AdminRoleEnum.ADMIN, comment="角色")
    phone = Column(String(20), comment="电话")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否启用")
    last_login = Column(DateTime, comment="最后登录时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    dorm_change_requests = relationship("DormChangeRequest", back_populates="admin")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="admin")
