from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Any
import logging

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.crud import crud_user
from app.utils import (
    generate_password_reset_token,
    verify_password_reset_token,
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=schemas.User)
def register(*, db: Session = Depends(deps.get_db), user_in: schemas.UserCreate) -> Any:
    """
    注册新用户
    
    - **email**: 用户邮箱（作为用户名）
    - **password**: 用户密码
    - **full_name**: 用户全名
    - **phone_number**: 电话号码（可选）
    - **preferences**: 用户偏好设置（可选）
    
    返回:
    - 创建的用户信息
    """
    user = crud.crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    user = crud.crud_user.create(db, obj_in=user_in)
    return user

@router.post("/login", response_model=schemas.Token)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用户登录
    
    - **username**: 用户邮箱
    - **password**: 用户密码
    
    返回:
    - access_token: 访问令牌
    - token_type: 令牌类型
    """
    user = crud.crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    } 