from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """登录请求模型"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """令牌载荷模型"""
    sub: int | None = None 