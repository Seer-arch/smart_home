from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Table, JSON, Enum, Date, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from app.db.session import Base
import json

# 用户-设备关联表
user_device = Table(
    'user_device',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('device_id', Integer, ForeignKey('devices.id'))
)

class DeviceType(str, enum.Enum):
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    CAMERA = "camera"
    DOOR_LOCK = "door_lock"
    SPEAKER = "speaker"
    SENSOR = "sensor"
    OTHER = "other"

class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class SecurityEventType(str, enum.Enum):
    MOTION_DETECTED = "motion_detected"
    DOOR_OPENED = "door_opened"
    WINDOW_OPENED = "window_opened"
    SMOKE_DETECTED = "smoke_detected"
    WATER_LEAK = "water_leak"
    TEMPERATURE_ALERT = "temperature_alert"
    OTHER = "other"

class FeedbackType(str, enum.Enum):
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    COMPLAINT = "complaint"
    OTHER = "other"

class FeedbackStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    phone_number = Column(String)
    preferences = Column(JSON, default=dict, server_default='{}')
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    houses = relationship("House", back_populates="owner", cascade="all, delete-orphan")
    device_usage_records = relationship("DeviceUsageRecord", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 添加外键
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    area = Column(Float, nullable=False)
    house_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    floor_count = Column(Integer)  # 楼层数
    room_count = Column(Integer)   # 房间数
    building_type = Column(String) # 建筑类型（公寓、别墅等）
    
    # 关系
    rooms = relationship("Room", back_populates="house", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="houses")
    security_events = relationship("SecurityEvent", back_populates="house", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.house_metadata, str):
            self.house_metadata = json.loads(self.house_metadata)

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    name = Column(String, nullable=False)
    area = Column(Float, nullable=False)  # 房间面积（平方米）
    room_type = Column(String, nullable=False)  # 房间类型
    description = Column(String)  # 房间描述
    room_metadata = Column(JSON, nullable=True)  # 元数据，使用 JSON 类型
    floor = Column(Integer, nullable=False, default=1)  # 所在楼层
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    house = relationship("House", back_populates="rooms")
    devices = relationship("Device", back_populates="room", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.room_metadata, str):
            self.room_metadata = json.loads(self.room_metadata)

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    manufacturer = Column(String)
    model = Column(String)
    serial_number = Column(String)
    installation_date = Column(Date)
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    description = Column(String)
    device_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    room = relationship("Room", back_populates="devices")
    usage_records = relationship("DeviceUsageRecord", back_populates="device", cascade="all, delete-orphan")
    maintenance_records = relationship("DeviceMaintenanceRecord", back_populates="device", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="device", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.device_metadata, str):
            self.device_metadata = json.loads(self.device_metadata)

class DeviceUsageRecord(Base):
    """设备使用记录"""
    __tablename__ = "device_usage_records"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Integer)  # 使用时长（分钟）
    energy_consumption = Column(Float)  # 能耗（kWh）
    usage_scenario = Column(String)  # 使用场景（如：日常使用、特殊活动等）
    usage_purpose = Column(String)  # 使用目的（如：制冷、加热、娱乐等）
    temperature = Column(Float)  # 使用时的环境温度
    humidity = Column(Float)  # 使用时的环境湿度
    is_automated = Column(Boolean, default=False)  # 是否自动控制
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    device = relationship("Device", back_populates="usage_records")
    user = relationship("User", back_populates="device_usage_records")

class DeviceMaintenanceRecord(Base):
    __tablename__ = "device_maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"))
    maintenance_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    description = Column(Text)
    cost = Column(Numeric(10, 2))
    maintenance_metadata = Column(JSON, nullable=True)  # 使用 JSON 类型
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    device = relationship("Device", back_populates="maintenance_records")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.maintenance_metadata, str):
            self.maintenance_metadata = json.loads(self.maintenance_metadata)

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    event_type = Column(String, nullable=False)
    event_time = Column(DateTime, nullable=False)
    description = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    status = Column(String, nullable=True)
    event_metadata = Column(JSON, nullable=True)  # 使用 JSON 类型
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    house = relationship("House", back_populates="security_events")
    device = relationship("Device", back_populates="security_events")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.event_metadata, str):
            self.event_metadata = json.loads(self.event_metadata)

class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    feedback_type = Column(String, nullable=False)  # 使用 FeedbackType 枚举
    status = Column(String, default=FeedbackStatus.PENDING)  # 使用 FeedbackStatus 枚举
    priority = Column(Integer, default=0)  # 优先级：0-低，1-中，2-高
    admin_response = Column(Text, nullable=True)  # 管理员回复
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="feedback")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read = Column(Boolean, default=False)
    notification_type = Column(String)  # 通知类型
    
    # 关系
    user = relationship("User", back_populates="notifications") 