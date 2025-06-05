from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class DeviceMaintenanceRecordBase(BaseModel):
    """设备维护记录基础模型"""
    device_id: int
    maintenance_type: str
    maintenance_date: datetime
    description: str
    cost: float
    maintenance_metadata: Optional[Dict[str, Any]] = None

class DeviceMaintenanceRecordCreate(DeviceMaintenanceRecordBase):
    """创建设备维护记录"""
    pass

class DeviceMaintenanceRecordUpdate(BaseModel):
    """更新设备维护记录"""
    maintenance_type: Optional[str] = None
    maintenance_date: Optional[datetime] = None
    description: Optional[str] = None
    cost: Optional[float] = None
    maintenance_metadata: Optional[Dict[str, Any]] = None

class DeviceMaintenanceRecord(DeviceMaintenanceRecordBase):
    """设备维护记录"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 