from datetime import datetime, timedelta
import random
import json
from sqlalchemy.orm import Session

from app.models.models import (
    User, House, Room, Device, DeviceUsageRecord, 
    DeviceMaintenanceRecord, UserFeedback, FeedbackType, FeedbackStatus
)
from app.core.security import get_password_hash

def create_test_data(db: Session):
    """创建测试数据"""
    # 创建用户
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        is_superuser=True,
        preferences={}  # 直接使用空字典
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 创建房屋
    house = House(
        user_id=user.id,
        name="测试房屋",
        address="测试地址",
        area=120.0,
        house_metadata={  # 直接使用字典
            "floor": 3,
            "rooms": 4,
            "bathrooms": 2,
            "year_built": 2020
        }
    )
    db.add(house)
    db.commit()
    db.refresh(house)

    # 创建房间
    rooms = [
        Room(
            house_id=house.id,
            name="客厅",
            room_type="living_room",
            area=30.0,
            room_metadata={  # 直接使用字典
                "windows": 2,
                "facing": "south",
                "flooring": "wood"
            }
        ),
        Room(
            house_id=house.id,
            name="主卧",
            room_type="bedroom",
            area=20.0,
            room_metadata={  # 直接使用字典
                "windows": 1,
                "facing": "east",
                "flooring": "carpet"
            }
        ),
        Room(
            house_id=house.id,
            name="厨房",
            room_type="kitchen",
            area=15.0,
            room_metadata={  # 直接使用字典
                "windows": 1,
                "facing": "north",
                "flooring": "tile"
            }
        )
    ]
    for room in rooms:
        db.add(room)
    db.commit()

    # 创建设备
    devices = [
        Device(
            room_id=rooms[0].id,
            name="智能空调",
            device_type="air_conditioner",
            status="online",
            device_metadata={  # 直接使用字典
                "brand": "格力",
                "model": "KFR-35GW",
                "power": 3500,
                "features": ["智能温控", "节能模式", "自清洁"]
            }
        ),
        Device(
            room_id=rooms[0].id,
            name="智能电视",
            device_type="tv",
            status="online",
            device_metadata={  # 直接使用字典
                "brand": "小米",
                "model": "L55M5",
                "resolution": "4K",
                "features": ["语音控制", "智能家居控制"]
            }
        ),
        Device(
            room_id=rooms[1].id,
            name="智能空调",
            device_type="air_conditioner",
            status="online",
            device_metadata={  # 直接使用字典
                "brand": "美的",
                "model": "KFR-26GW",
                "power": 2600,
                "features": ["智能温控", "睡眠模式"]
            }
        ),
        Device(
            room_id=rooms[2].id,
            name="智能冰箱",
            device_type="refrigerator",
            status="online",
            device_metadata={  # 直接使用字典
                "brand": "海尔",
                "model": "BCD-452WDPF",
                "capacity": 452,
                "features": ["智能控温", "食材管理"]
            }
        )
    ]
    for device in devices:
        db.add(device)
    db.commit()

    # 创建设备使用记录
    now = datetime.utcnow()
    usage_scenarios = ["日常使用", "特殊活动", "节能模式", "舒适模式"]
    usage_purposes = ["制冷", "制热", "娱乐", "食物保鲜"]
    
    for device in devices:
        # 生成过去30天的使用记录
        for day in range(30):
            # 每天生成2-5条使用记录
            for _ in range(random.randint(2, 5)):
                start_time = now - timedelta(days=day, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                duration = random.randint(30, 180)  # 30分钟到3小时
                end_time = start_time + timedelta(minutes=duration)
                
                # 根据设备类型设置使用场景和目的
                if device.device_type == "air_conditioner":
                    usage_scenario = random.choice(["日常使用", "节能模式", "舒适模式"])
                    usage_purpose = random.choice(["制冷", "制热"])
                    temperature = random.uniform(20, 30)
                    humidity = random.uniform(30, 70)
                elif device.device_type == "tv":
                    usage_scenario = random.choice(["日常使用", "特殊活动"])
                    usage_purpose = "娱乐"
                    temperature = random.uniform(22, 26)
                    humidity = random.uniform(40, 60)
                else:  # refrigerator
                    usage_scenario = "日常使用"
                    usage_purpose = "食物保鲜"
                    temperature = random.uniform(18, 22)
                    humidity = random.uniform(50, 60)

                # 计算能耗（根据设备类型和持续时间）
                if device.device_type == "air_conditioner":
                    power = device.device_metadata["power"]  # 直接访问字典
                    energy_consumption = (power * duration / 60) / 1000  # 转换为kWh
                elif device.device_type == "tv":
                    energy_consumption = (150 * duration / 60) / 1000  # 假设150W功率
                else:  # refrigerator
                    energy_consumption = (100 * duration / 60) / 1000  # 假设100W功率

                record = DeviceUsageRecord(
                    device_id=device.id,
                    user_id=user.id,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    energy_consumption=energy_consumption,
                    usage_scenario=usage_scenario,
                    usage_purpose=usage_purpose,
                    temperature=temperature,
                    humidity=humidity,
                    is_automated=random.choice([True, False])
                )
                db.add(record)
    
    db.commit()

    return {
        "user": user,
        "house": house,
        "rooms": rooms,
        "devices": devices
    } 