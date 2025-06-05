from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.models.models import FeedbackType, FeedbackStatus

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserFeedbackBase(BaseModel):
    content: str
    feedback_type: FeedbackType
    priority: Optional[int] = 0

class UserFeedbackCreate(UserFeedbackBase):
    pass

class UserFeedbackUpdate(BaseModel):
    content: Optional[str] = None
    feedback_type: Optional[FeedbackType] = None
    status: Optional[FeedbackStatus] = None
    priority: Optional[int] = None
    admin_response: Optional[str] = None

class UserFeedback(UserFeedbackBase):
    id: int
    user_id: int
    status: FeedbackStatus
    admin_response: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserFeedbackResponse(UserFeedback):
    user_email: str
    user_full_name: Optional[str] = None

class HouseBase(BaseModel):
    name: str
    address: str
    area: float
    house_metadata: Optional[Dict[str, Any]] = None

class HouseCreate(HouseBase):
    pass

class HouseUpdate(HouseBase):
    name: Optional[str] = None
    address: Optional[str] = None
    area: Optional[float] = None

class House(HouseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RoomBase(BaseModel):
    name: str
    area: float
    room_type: str
    description: Optional[str] = None
    room_metadata: Optional[Dict[str, Any]] = None
    floor: int = 1

class RoomCreate(RoomBase):
    house_id: int

class RoomUpdate(RoomBase):
    name: Optional[str] = None
    area: Optional[float] = None
    room_type: Optional[str] = None

class Room(RoomBase):
    id: int
    house_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DeviceBase(BaseModel):
    name: str
    device_type: str
    status: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[date] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    description: Optional[str] = None
    device_metadata: Optional[Dict[str, Any]] = None

class DeviceCreate(DeviceBase):
    room_id: int

class DeviceUpdate(DeviceBase):
    name: Optional[str] = None
    device_type: Optional[str] = None
    status: Optional[str] = None

class Device(DeviceBase):
    id: int
    room_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

class DeviceMaintenanceRecordBase(BaseModel):
    maintenance_date: datetime
    maintenance_type: str
    description: Optional[str] = None
    cost: Optional[float] = None
    maintenance_metadata: Optional[Dict[str, Any]] = None

class DeviceMaintenanceRecordCreate(DeviceMaintenanceRecordBase):
    device_id: int

class DeviceMaintenanceRecordUpdate(DeviceMaintenanceRecordBase):
    pass

class DeviceMaintenanceRecord(DeviceMaintenanceRecordBase):
    id: int
    device_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SecurityEventBase(BaseModel):
    event_type: str
    event_time: datetime
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = None

class SecurityEventCreate(SecurityEventBase):
    house_id: int
    device_id: Optional[int] = None

class SecurityEventUpdate(SecurityEventBase):
    pass

class SecurityEvent(SecurityEventBase):
    id: int
    house_id: int
    device_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 