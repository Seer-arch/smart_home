from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import json

from app.core.deps import get_current_active_user, get_db
from app.models.models import User, Device, DeviceUsageRecord, House, Room, DeviceMaintenanceRecord
from app.schemas.analytics import (
    DeviceUsageStats,
    UserHabitsAnalysis,
    EnergyConsumptionAnalysis,
    DeviceHealthAnalysis,
    SecurityAnalysis,
    DeviceTimeAnalysis,
    DeviceCorrelationAnalysis,
    HouseAreaImpactAnalysis
)

router = APIRouter()

@router.get("/devices/usage", response_model=List[DeviceUsageStats])
def analyze_device_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 30
):
    """
    分析设备使用情况
    """
    # 获取用户的所有房屋
    houses = db.query(House).filter(House.user_id == current_user.id).all()
    if not houses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到用户的房屋"
        )
    
    # 获取时间范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取所有设备的使用记录
    usage_records = db.query(
        Device.id,
        Device.name,
        Device.device_type,
        func.count(DeviceUsageRecord.id).label('usage_count'),
        func.sum(DeviceUsageRecord.duration).label('total_duration'),
        func.sum(DeviceUsageRecord.energy_consumption).label('total_energy')
    ).join(
        DeviceUsageRecord,
        Device.id == DeviceUsageRecord.device_id
    ).join(
        Room,
        Device.room_id == Room.id
    ).join(
        House,
        Room.house_id == House.id
    ).filter(
        House.user_id == current_user.id,
        DeviceUsageRecord.start_time >= start_date,
        DeviceUsageRecord.start_time <= end_date
    ).group_by(
        Device.id,
        Device.name,
        Device.device_type
    ).all()
    
    return [
        DeviceUsageStats(
            device_id=record.id,
            device_name=record.name,
            device_type=record.device_type,
            usage_count=record.usage_count,
            total_duration=record.total_duration or 0,
            total_energy=record.total_energy or 0
        )
        for record in usage_records
    ]

@router.get("/user/habits", response_model=UserHabitsAnalysis)
def analyze_user_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 30
):
    """
    分析用户使用习惯
    """
    # 获取时间范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取用户的所有设备使用记录
    usage_records = db.query(DeviceUsageRecord).filter(
        DeviceUsageRecord.user_id == current_user.id,
        DeviceUsageRecord.start_time >= start_date,
        DeviceUsageRecord.start_time <= end_date
    ).all()
    
    # 分析使用时间分布
    time_distribution = {}
    for record in usage_records:
        hour = record.start_time.hour
        time_distribution[hour] = time_distribution.get(hour, 0) + 1
    
    # 分析最常使用的设备
    device_usage = {}
    for record in usage_records:
        device = db.query(Device).filter(Device.id == record.device_id).first()
        if device:
            device_usage[device.name] = device_usage.get(device.name, 0) + 1
    
    return UserHabitsAnalysis(
        time_distribution=time_distribution,
        most_used_devices=device_usage,
        total_usage_time=sum(record.duration or 0 for record in usage_records),
        average_daily_usage=sum(record.duration or 0 for record in usage_records) / days
    )

@router.get("/energy/consumption", response_model=EnergyConsumptionAnalysis)
def analyze_energy_consumption(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 30
):
    """
    分析能源消耗情况
    """
    # 获取时间范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取所有设备的能源消耗记录
    energy_records = db.query(
        Device.id,
        Device.name,
        func.sum(DeviceUsageRecord.energy_consumption).label('total_energy')
    ).join(
        DeviceUsageRecord,
        Device.id == DeviceUsageRecord.device_id
    ).join(
        Room,
        Device.room_id == Room.id
    ).join(
        House,
        Room.house_id == House.id
    ).filter(
        House.user_id == current_user.id,
        DeviceUsageRecord.start_time >= start_date,
        DeviceUsageRecord.start_time <= end_date
    ).group_by(
        Device.id,
        Device.name
    ).all()
    
    # 计算总能耗和每日平均能耗
    total_energy = sum(record.total_energy or 0 for record in energy_records)
    daily_average = total_energy / days if days > 0 else 0
    
    return EnergyConsumptionAnalysis(
        total_consumption=total_energy,
        daily_average=daily_average,
        device_consumption={
            record.name: record.total_energy or 0
            for record in energy_records
        }
    )

@router.get("/devices/health", response_model=List[DeviceHealthAnalysis])
def analyze_device_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    分析设备健康状态
    """
    # 获取用户的所有设备
    devices = db.query(Device).join(
        Room,
        Device.room_id == Room.id
    ).join(
        House,
        Room.house_id == House.id
    ).filter(
        House.user_id == current_user.id
    ).all()
    
    health_analysis = []
    for device in devices:
        # 获取设备最近的使用记录
        recent_usage = db.query(DeviceUsageRecord).filter(
            DeviceUsageRecord.device_id == device.id
        ).order_by(
            desc(DeviceUsageRecord.start_time)
        ).first()
        
        # 获取设备最近的维护记录
        recent_maintenance = db.query(DeviceMaintenanceRecord).filter(
            DeviceMaintenanceRecord.device_id == device.id
        ).order_by(
            desc(DeviceMaintenanceRecord.maintenance_date)
        ).first()
        
        # 计算健康分数
        health_score = calculate_health_score(device, recent_usage, recent_maintenance)
        
        health_analysis.append(
            DeviceHealthAnalysis(
                device_id=device.id,
                device_name=device.name,
                status=device.status,
                last_usage=recent_usage.start_time if recent_usage else None,
                last_maintenance=recent_maintenance.maintenance_date if recent_maintenance else None,
                health_score=health_score
            )
        )
    
    return health_analysis

def calculate_health_score(device, recent_usage, recent_maintenance):
    """
    计算设备健康分数
    """
    score = 100.0
    
    # 根据设备状态调整分数
    if device.status == "offline":
        score -= 30
    elif device.status == "error":
        score -= 50
    elif device.status == "maintenance":
        score -= 20
    
    # 根据最近使用情况调整分数
    if recent_usage:
        days_since_last_usage = (datetime.utcnow() - recent_usage.start_time).days
        if days_since_last_usage > 30:
            score -= 10
    
    # 根据最近维护情况调整分数
    if recent_maintenance:
        days_since_last_maintenance = (datetime.utcnow() - recent_maintenance.maintenance_date).days
        if days_since_last_maintenance > 180:  # 超过6个月未维护
            score -= 20
    
    return max(0, min(100, score))  # 确保分数在0-100之间

@router.get("/devices/usage-frequency", response_model=List[DeviceUsageStats])
def analyze_device_usage_frequency(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 30
):
    """
    分析设备使用频率
    """
    # 获取时间范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取用户的所有设备使用记录
    usage_stats = db.query(
        Device.id,
        Device.name,
        Device.device_type,
        func.count(DeviceUsageRecord.id).label('usage_count'),
        func.avg(DeviceUsageRecord.duration).label('avg_duration'),
        func.sum(DeviceUsageRecord.energy_consumption).label('total_energy')
    ).join(
        DeviceUsageRecord,
        Device.id == DeviceUsageRecord.device_id
    ).join(
        Room,
        Device.room_id == Room.id
    ).join(
        House,
        Room.house_id == House.id
    ).filter(
        House.user_id == current_user.id,
        DeviceUsageRecord.start_time >= start_date,
        DeviceUsageRecord.start_time <= end_date
    ).group_by(
        Device.id,
        Device.name,
        Device.device_type
    ).all()
    
    return [
        DeviceUsageStats(
            device_id=stat.id,
            device_name=stat.name,
            device_type=stat.device_type,
            usage_count=stat.usage_count,
            total_duration=stat.avg_duration or 0,
            total_energy=stat.total_energy or 0
        )
        for stat in usage_stats
    ]

@router.get("/devices/usage-time", response_model=DeviceTimeAnalysis)
def analyze_device_usage_time(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 30
):
    """
    分析设备使用时间段
    """
    # 获取时间范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取用户的所有设备使用记录
    usage_records = db.query(DeviceUsageRecord).join(
        Device,
        DeviceUsageRecord.device_id == Device.id
    ).join(
        Room,
        Device.room_id == Room.id
    ).join(
        House,
        Room.house_id == House.id
    ).filter(
        House.user_id == current_user.id,
        DeviceUsageRecord.start_time >= start_date,
        DeviceUsageRecord.start_time <= end_date
    ).all()
    
    # 按小时统计使用次数
    hourly_usage = {hour: 0 for hour in range(24)}
    for record in usage_records:
        hour = record.start_time.hour
        hourly_usage[hour] += 1
    
    # 按设备类型统计使用次数
    device_type_usage = {}
    for record in usage_records:
        device = db.query(Device).filter(Device.id == record.device_id).first()
        if device:
            device_type = device.device_type
            if device_type not in device_type_usage:
                device_type_usage[device_type] = {hour: 0 for hour in range(24)}
            hour = record.start_time.hour
            device_type_usage[device_type][hour] += 1
    
    return DeviceTimeAnalysis(
        hourly_usage=hourly_usage,
        device_type_usage=device_type_usage
    )

@router.get("/devices/correlation", response_model=DeviceCorrelationAnalysis)
def analyze_device_correlation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 30,
    time_window: int = 5  # 时间窗口（分钟）
):
    """
    分析设备之间的使用关联性
    """
    # 获取时间范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取用户的所有设备使用记录
    usage_records = db.query(DeviceUsageRecord).join(
        Device,
        DeviceUsageRecord.device_id == Device.id
    ).join(
        Room,
        Device.room_id == Room.id
    ).join(
        House,
        Room.house_id == House.id
    ).filter(
        House.user_id == current_user.id,
        DeviceUsageRecord.start_time >= start_date,
        DeviceUsageRecord.start_time <= end_date
    ).order_by(
        DeviceUsageRecord.start_time
    ).all()
    
    # 分析设备同时使用情况
    correlations = []
    for i, record1 in enumerate(usage_records):
        device1 = db.query(Device).filter(Device.id == record1.device_id).first()
        if not device1:
            continue
            
        for record2 in usage_records[i+1:]:
            device2 = db.query(Device).filter(Device.id == record2.device_id).first()
            if not device2:
                continue
                
            # 检查两个设备的使用时间是否在时间窗口内
            time_diff = abs((record2.start_time - record1.start_time).total_seconds() / 60)
            if time_diff <= time_window:
                correlations.append({
                    "device1": device1.name,
                    "device2": device2.name,
                    "time1": record1.start_time,
                    "time2": record2.start_time,
                    "time_diff": time_diff
                })
    
    # 统计设备关联次数
    correlation_count = {}
    for corr in correlations:
        key = f"{corr['device1']}-{corr['device2']}"
        correlation_count[key] = correlation_count.get(key, 0) + 1
    
    return DeviceCorrelationAnalysis(
        correlations=correlations,
        correlation_count=correlation_count
    )

@router.get("/house/area-impact", response_model=HouseAreaImpactAnalysis)
def analyze_house_area_impact(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 30
):
    """
    分析房屋面积对设备使用行为的影响
    """
    # 获取时间范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取用户的所有房屋
    houses = db.query(House).filter(House.user_id == current_user.id).all()
    
    house_stats = []
    for house in houses:
        # 获取房屋的所有设备使用记录
        usage_stats = db.query(
            Device.device_type,
            func.count(DeviceUsageRecord.id).label('usage_count'),
            func.sum(DeviceUsageRecord.energy_consumption).label('total_energy')
        ).join(
            DeviceUsageRecord,
            Device.id == DeviceUsageRecord.device_id
        ).join(
            Room,
            Device.room_id == Room.id
        ).filter(
            Room.house_id == house.id,
            DeviceUsageRecord.start_time >= start_date,
            DeviceUsageRecord.start_time <= end_date
        ).group_by(
            Device.device_type
        ).all()
        
        # 计算每平方米的使用频率和能耗
        device_stats = []
        for stat in usage_stats:
            usage_per_sqm = stat.usage_count / house.area if house.area > 0 else 0
            energy_per_sqm = stat.total_energy / house.area if house.area > 0 else 0
            
            device_stats.append({
                "type": stat.device_type,
                "usage_count": stat.usage_count,
                "total_energy": stat.total_energy or 0,
                "usage_per_sqm": usage_per_sqm,
                "energy_per_sqm": energy_per_sqm
            })
        
        house_stats.append({
            "house_id": house.id,
            "house_name": house.name,
            "area": house.area,
            "device_stats": device_stats
        })
    
    return HouseAreaImpactAnalysis(house_stats=house_stats) 