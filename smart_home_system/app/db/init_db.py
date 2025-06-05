import logging
import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import Base, engine
from app.crud.crud_user import crud_user
from app.schemas.user import UserCreate
from app.core.config import settings
from app.models.models import User, House, Room, Device, DeviceUsageRecord, UserFeedback, DeviceMaintenanceRecord, SecurityEvent
from app.db.init_test_data import create_test_data
from app.db.session import SessionLocal

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> bool:
    """初始化数据库"""
    try:
        logger.info("正在初始化数据库...")
        
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        logger.info("已清空数据库")
        
        # 按顺序创建表
        tables = [
            User.__table__,
            House.__table__,
            Room.__table__,
            Device.__table__,
            DeviceUsageRecord.__table__,
            DeviceMaintenanceRecord.__table__,
            SecurityEvent.__table__,
            UserFeedback.__table__
        ]
        
        for table in tables:
            table.create(bind=engine)
            logger.info(f"创建表 {table.name} 成功")
        
        logger.info("所有数据库表创建成功")
        
        # 创建测试数据
        return create_test_data(db)
    except Exception as e:
        logger.error(f"创建数据库表时出错: {e}")
        return False

if __name__ == "__main__":
    print("创建测试数据...")
    db = SessionLocal()
    try:
        init_db(db)
        print("测试数据创建完成！")
    finally:
        db.close() 