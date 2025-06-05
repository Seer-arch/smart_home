from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.core.deps import get_current_active_user, get_db
from app.models.models import User, Device, DeviceMaintenanceRecord, Room, House
from app.schemas.device_maintenance import (
    DeviceMaintenanceRecordCreate,
    DeviceMaintenanceRecordUpdate,
    DeviceMaintenanceRecord as DeviceMaintenanceRecordSchema
)

router = APIRouter()

@router.post("/", response_model=DeviceMaintenanceRecordSchema)
def create_device_maintenance_record(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    record_in: DeviceMaintenanceRecordCreate
):
    """
    创建设备维护记录
    """
    # 验证设备是否存在且属于当前用户
    device = db.query(Device).join(
        Room
    ).join(
        House
    ).filter(
        Device.id == record_in.device_id,
        House.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在或不属于当前用户"
        )
    
    # 创建维护记录
    db_record = DeviceMaintenanceRecord(
        device_id=record_in.device_id,
        maintenance_type=record_in.maintenance_type,
        maintenance_date=record_in.maintenance_date,
        description=record_in.description,
        cost=record_in.cost,
        maintenance_metadata=record_in.maintenance_metadata
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/", response_model=List[DeviceMaintenanceRecordSchema])
def get_device_maintenance_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    device_id: Optional[int] = None,
    maintenance_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    获取设备维护记录列表
    """
    query = db.query(DeviceMaintenanceRecord).join(
        Device
    ).join(
        Room
    ).join(
        House
    ).filter(
        House.user_id == current_user.id
    )
    
    if device_id:
        query = query.filter(DeviceMaintenanceRecord.device_id == device_id)
    if maintenance_type:
        query = query.filter(DeviceMaintenanceRecord.maintenance_type == maintenance_type)
    
    records = query.order_by(
        DeviceMaintenanceRecord.maintenance_date.desc()
    ).offset(skip).limit(limit).all()
    
    return records

@router.get("/{record_id}", response_model=DeviceMaintenanceRecordSchema)
def get_device_maintenance_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个设备维护记录
    """
    record = db.query(DeviceMaintenanceRecord).join(
        Device
    ).join(
        Room
    ).join(
        House
    ).filter(
        DeviceMaintenanceRecord.id == record_id,
        House.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维护记录不存在或不属于当前用户"
        )
    
    return record

@router.put("/{record_id}", response_model=DeviceMaintenanceRecordSchema)
def update_device_maintenance_record(
    record_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    record_in: DeviceMaintenanceRecordUpdate
):
    """
    更新设备维护记录
    """
    record = db.query(DeviceMaintenanceRecord).join(
        Device
    ).join(
        Room
    ).join(
        House
    ).filter(
        DeviceMaintenanceRecord.id == record_id,
        House.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维护记录不存在或不属于当前用户"
        )
    
    # 更新记录
    update_data = record_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.delete("/{record_id}", response_model=DeviceMaintenanceRecordSchema)
def delete_device_maintenance_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除设备维护记录
    """
    record = db.query(DeviceMaintenanceRecord).join(
        Device
    ).join(
        Room
    ).join(
        House
    ).filter(
        DeviceMaintenanceRecord.id == record_id,
        House.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维护记录不存在或不属于当前用户"
        )
    
    # 保存要返回的记录副本
    record_copy = record
    
    # 删除记录
    db.delete(record)
    db.commit()
    
    return record_copy 