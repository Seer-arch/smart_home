from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, field_validator
import json

class DeviceUsageRecordBase(BaseModel):
    """设备使用记录基础模型"""
    device_id: int
    start_time: datetime
    end_time: datetime
    energy_consumption: float
    usage_metadata: Optional[Dict[str, Any]] = None

    @field_validator('usage_metadata', mode='before')
    @classmethod
    def parse_usage_metadata(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v

class DeviceUsageRecordCreate(DeviceUsageRecordBase):
    """创建设备使用记录"""
    pass

class DeviceUsageRecordUpdate(BaseModel):
    """更新设备使用记录"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    energy_consumption: Optional[float] = None
    usage_metadata: Optional[Dict[str, Any]] = None

    @field_validator('usage_metadata', mode='before')
    @classmethod
    def parse_usage_metadata(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v

class DeviceUsageRecord(DeviceUsageRecordBase):
    """设备使用记录"""
    id: int
    user_id: int
    duration: int
    usage_scenario: str
    usage_purpose: str
    temperature: float
    humidity: float
    is_automated: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    } 