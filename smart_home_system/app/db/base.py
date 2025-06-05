from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.models import User, House, Room, Device, DeviceUsageRecord, UserFeedback  # noqa
from app.models.room import Room  # 确保 Room 模型被正确导入 