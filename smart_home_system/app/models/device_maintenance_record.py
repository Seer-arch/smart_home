from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class DeviceMaintenanceRecord(Base):
    __tablename__ = "device_maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"))
    maintenance_date = Column(Date, nullable=False)
    maintenance_type = Column(String, nullable=False)
    description = Column(String)
    cost = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    device = relationship("Device", back_populates="maintenance_records") 