import logging
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.init_data import init_test_data
from app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_db() -> bool:
    """重置数据库（仅用于开发环境）
    
    Returns:
        bool: 重置是否成功
    """
    if settings.ENV != "development":
        logger.error("此操作仅允许在开发环境中执行")
        return False
        
    try:
        # 删除所有表
        logger.info("删除所有表...")
        Base.metadata.drop_all(bind=engine)
        logger.info("表删除成功")
        
        # 重新创建表
        logger.info("重新创建表...")
        Base.metadata.create_all(bind=engine)
        logger.info("表创建成功")
        
        # 初始化测试数据
        logger.info("初始化测试数据...")
        db = SessionLocal()
        try:
            init_test_data(db)
            logger.info("测试数据初始化成功")
            return True
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"数据库重置出错: {str(e)}")
        return False

if __name__ == "__main__":
    reset_db() 