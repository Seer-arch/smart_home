from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id", ondelete="CASCADE"))
    event_type = Column(String, nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)
    description = Column(String)
    severity = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    # 关系
    house = relationship("House", back_populates="security_events")
    device = relationship("Device", back_populates="security_events")