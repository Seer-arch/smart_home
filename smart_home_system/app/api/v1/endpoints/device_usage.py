from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.deps import get_current_active_user, get_db
from app.models.models import User, Device, DeviceUsageRecord, Room, House
from app.schemas.device_usage import (
    DeviceUsageRecordCreate,
    DeviceUsageRecordUpdate,
    DeviceUsageRecord as DeviceUsageRecordSchema
)

router = APIRouter()

@router.post("/", response_model=DeviceUsageRecordSchema)
def create_device_usage_record(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    record_in: DeviceUsageRecordCreate
):
    """
    创建设备使用记录
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
    
    # 创建使用记录
    db_record = DeviceUsageRecord(
        device_id=record_in.device_id,
        user_id=current_user.id,
        start_time=record_in.start_time,
        end_time=record_in.end_time,
        duration=int((record_in.end_time - record_in.start_time).total_seconds() / 60),  # 计算使用时长（分钟）
        energy_consumption=record_in.energy_consumption,
        usage_scenario=record_in.usage_metadata.get("usage_scenario", "日常使用") if record_in.usage_metadata else "日常使用",
        usage_purpose=record_in.usage_metadata.get("usage_purpose", "其他") if record_in.usage_metadata else "其他",
        temperature=record_in.usage_metadata.get("temperature", 25.0) if record_in.usage_metadata else 25.0,
        humidity=record_in.usage_metadata.get("humidity", 50.0) if record_in.usage_metadata else 50.0,
        is_automated=record_in.usage_metadata.get("is_automated", False) if record_in.usage_metadata else False
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/", response_model=List[DeviceUsageRecordSchema])
def get_device_usage_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    device_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    获取设备使用记录列表
    """
    query = db.query(DeviceUsageRecord).join(
        Device
    ).join(
        Room
    ).join(
        House
    ).filter(
        House.user_id == current_user.id
    )
    
    if device_id:
        query = query.filter(DeviceUsageRecord.device_id == device_id)
    if start_date:
        query = query.filter(DeviceUsageRecord.start_time >= start_date)
    if end_date:
        query = query.filter(DeviceUsageRecord.end_time <= end_date)
    
    records = query.order_by(
        DeviceUsageRecord.start_time.desc()
    ).offset(skip).limit(limit).all()
    
    return records

@router.get("/{record_id}", response_model=DeviceUsageRecordSchema)
def get_device_usage_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个设备使用记录
    """
    record = db.query(DeviceUsageRecord).join(
        Device
    ).join(
        Room
    ).join(
        House
    ).filter(
        DeviceUsageRecord.id == record_id,
        House.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用记录不存在或不属于当前用户"
        )
    
    return record

@router.put("/{record_id}", response_model=DeviceUsageRecordSchema)
def update_device_usage_record(
    record_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    record_in: DeviceUsageRecordUpdate
):
    """
    更新设备使用记录
    """
    record = db.query(DeviceUsageRecord).join(
        Device
    ).join(
        Room
    ).join(
        House
    ).filter(
        DeviceUsageRecord.id == record_id,
        House.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用记录不存在或不属于当前用户"
        )
    
    # 更新记录
    for field, value in record_in.dict(exclude_unset=True).items():
        setattr(record, field, value)
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.delete("/{record_id}", response_model=DeviceUsageRecordSchema)
def delete_device_usage_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除设备使用记录
    """
    record = db.query(DeviceUsageRecord).join(
        Device
    ).join(
        Room
    ).join(
        House
    ).filter(
        DeviceUsageRecord.id == record_id,
        House.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用记录不存在或不属于当前用户"
        )
    
    db.delete(record)
    db.commit()
    return record 