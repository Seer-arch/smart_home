from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    area = Column(Float, nullable=False)
    room_type = Column(String, nullable=False)
    description = Column(String)
    room_metadata = Column(JSON)  # 使用 JSON 类型
    floor = Column(Integer, nullable=False, default=1)  # 添加 floor 字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    house = relationship("House", back_populates="rooms")
    devices = relationship("Device", back_populates="room", cascade="all, delete-orphan") 