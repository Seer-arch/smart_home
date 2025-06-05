import os
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # 项目基本信息
    PROJECT_NAME: str = "智能家居系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"  # 请在生产环境中更改
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./smart_home.db"
    
    # 超级用户配置
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    # 环境配置
    ENV: str = "development"
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # 静态文件配置
    STATIC_DIR: Path = Path("app/static")
    TEMPLATES_DIR: Path = Path("app/templates")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# 创建全局设置对象
settings = Settings() 