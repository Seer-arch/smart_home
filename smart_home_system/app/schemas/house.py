from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class HouseBase(BaseModel):
    """房屋基础模型"""
    name: str
    address: str
    area: float
    description: Optional[str] = None
    house_metadata: Optional[Dict[str, Any]] = None
    floor_count: Optional[int] = None
    room_count: Optional[int] = None
    building_type: Optional[str] = None

class HouseCreate(HouseBase):
    """房屋创建模型"""
    pass

class HouseUpdate(HouseBase):
    """房屋更新模型"""
    pass

class House(HouseBase):
    """房屋模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 