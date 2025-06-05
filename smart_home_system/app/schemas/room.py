from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class RoomBase(BaseModel):
    """房间基础模型"""
    name: str
    area: float
    room_type: str
    description: Optional[str] = None
    room_metadata: Optional[Dict[str, Any]] = None
    floor: Optional[int] = 1

class RoomCreate(RoomBase):
    """房间创建模型"""
    house_id: int

class RoomUpdate(RoomBase):
    """房间更新模型"""
    pass

class Room(RoomBase):
    """房间模型"""
    id: int
    house_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 