from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class DeviceUsageRecord(Base):
    __tablename__ = "device_usage_records"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    energy_consumption = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    device = relationship("Device", back_populates="usage_records") 