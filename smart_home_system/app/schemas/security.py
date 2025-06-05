from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class SecurityEventBase(BaseModel):
    """安全事件基础模型"""
    house_id: int
    device_id: Optional[int] = None
    event_type: str
    event_time: datetime
    description: str
    severity: str
    status: str
    event_metadata: Optional[Dict[str, Any]] = None

class SecurityEventCreate(SecurityEventBase):
    """创建安全事件"""
    pass

class SecurityEventUpdate(BaseModel):
    """更新安全事件"""
    device_id: Optional[int] = None
    event_type: Optional[str] = None
    event_time: Optional[datetime] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = None

class SecurityEvent(SecurityEventBase):
    """安全事件"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 
        from_attributes = True 