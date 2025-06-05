from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.models import User
from app.schemas.token import TokenPayload

logger = logging.getLogger(__name__)

# OAuth2 scheme
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    获取当前用户
    
    Args:
        db: 数据库会话
        token: JWT令牌
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 认证失败时抛出
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 记录 token 验证过程
        logger.info("开始验证访问令牌")
        
        # 解码 token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_iat": True, "verify_exp": True}
        )
        
        logger.info(f"Token 解码成功，载荷: {payload}")
        
        # 验证 token 数据
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            logger.error("Token 中缺少用户ID")
            raise credentials_exception
            
        if payload.get("type") != "access":
            logger.error("Token 类型错误")
            raise credentials_exception
            
        logger.info(f"Token 验证成功，用户ID: {token_data.sub}")
        
    except JWTError as e:
        logger.error(f"JWT 验证失败: {str(e)}")
        raise credentials_exception
    except ValidationError as e:
        logger.error(f"Token 数据验证失败: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Token 验证过程发生未知错误: {str(e)}")
        raise credentials_exception
    
    try:
        # 查询用户
        user_id = int(token_data.sub)  # 将字符串ID转换为整数
        logger.info(f"开始查询用户信息，用户ID: {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.error(f"用户不存在: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
            
        if not user.is_active:
            logger.error(f"用户未激活: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户未激活"
            )
            
        logger.info(f"成功获取用户信息: {user.email}")
        return user
        
    except ValueError as e:
        logger.error(f"用户ID格式错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的用户ID格式"
        )
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        User: 当前活跃用户对象
        
    Raises:
        HTTPException: 用户未激活时抛出
    """
    try:
        if not current_user.is_active:
            logger.error(f"用户未激活: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户未激活"
            )
        return current_user
    except Exception as e:
        logger.error(f"验证用户状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证用户状态失败"
        ) 