from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date

class DeviceBase(BaseModel):
    """设备基础模型"""
    name: str
    device_type: str
    status: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[date] = None
    description: Optional[str] = None
    device_metadata: Optional[Dict[str, Any]] = None

class DeviceCreate(DeviceBase):
    """设备创建模型"""
    room_id: int

class DeviceUpdate(DeviceBase):
    """设备更新模型"""
    pass

class Device(DeviceBase):
    """设备模型"""
    id: int
    room_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 