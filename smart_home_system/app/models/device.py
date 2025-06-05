from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    manufacturer = Column(String)
    model = Column(String)
    serial_number = Column(String)
    installation_date = Column(Date)
    last_maintenance_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    room = relationship("Room", back_populates="devices")
    usage_records = relationship("DeviceUsageRecord", back_populates="device", cascade="all, delete-orphan")
    maintenance_records = relationship("DeviceMaintenanceRecord", back_populates="device", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="device", cascade="all, delete-orphan")