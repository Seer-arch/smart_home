from typing import Optional, Dict, Any
from datetime import datetime
import json
from pydantic import BaseModel, EmailStr, Field, field_validator

# 基础用户模型
class UserBase(BaseModel):
    """用户基础模型"""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator('preferences')
    def validate_preferences(cls, v):
        """验证preferences字段"""
        if v is None:
            return {}
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        if isinstance(v, dict):
            return v
        return {}

# 创建用户时的请求模型
class UserCreate(UserBase):
    """用户创建模型"""
    email: EmailStr
    password: str

# 更新用户时的请求模型
class UserUpdate(UserBase):
    """用户更新模型"""
    password: Optional[str] = None

# 数据库中的用户模型
class UserInDBBase(UserBase):
    """数据库中的用户基础模型"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# API响应中的用户模型
class User(UserInDBBase):
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

# 用户登录请求模型
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 用户登录响应模型
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class UserInDB(UserInDBBase):
    """数据库中的用户模型"""
    hashed_password: str 