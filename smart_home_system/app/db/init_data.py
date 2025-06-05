from datetime import datetime, timedelta, date
import random
from sqlalchemy.orm import Session

from app.models.models import User, House, Room, Device, DeviceUsageRecord, DeviceMaintenanceRecord
from app.core.security import get_password_hash

def init_test_data(db: Session) -> None:
    """初始化测试数据"""
    
    # 1. 创建测试用户
    test_user = User(
        email="test@example.com",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        full_name="测试用户",
        phone_number="13800138000",
        preferences='{"theme": "light", "language": "zh"}'
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # 2. 创建房屋
    test_house = House(
        name="测试房屋",
        address="测试地址",
        area=100.0,
        user_id=test_user.id
    )
    db.add(test_house)
    db.commit()
    db.refresh(test_house)
    
    # 3. 创建房间
    test_room = Room(
        name="客厅",
        room_type="living_room",
        area=30.0,
        house_id=test_house.id
    )
    db.add(test_room)
    db.commit()
    db.refresh(test_room)
    
    # 4. 创建设备
    test_device = Device(
        name="智能灯",
        device_type="light",
        status="online",
        room_id=test_room.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(test_device)
    db.commit()
    db.refresh(test_device)
    
    # 5. 创建设备使用记录
    for i in range(5):
        start_time = datetime.utcnow() - timedelta(hours=i)
        end_time = start_time + timedelta(minutes=30)
        usage_record = DeviceUsageRecord(
            device_id=test_device.id,
            start_time=start_time,
            end_time=end_time,
            energy_consumption=5.0,
            status="completed",
            usage_metadata={"temperature": 25, "humidity": 50}
        )
        db.add(usage_record)
    
    # 创建设备维护记录
    maintenance_record = DeviceMaintenanceRecord(
        device_id=test_device.id,
        maintenance_date=datetime.utcnow() - timedelta(days=7),
        maintenance_type="定期检查",
        description="常规维护检查",
        cost=0.0
    )
    db.add(maintenance_record)
    
    # 提交所有更改
    db.commit()
    
    return {
        "user": test_user,
        "house": test_house,
        "rooms": [test_room],
        "devices": [test_device]
    } 