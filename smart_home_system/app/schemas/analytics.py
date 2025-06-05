from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class DeviceUsageStats(BaseModel):
    device_id: int
    device_name: str
    device_type: str
    usage_count: int
    total_duration: float
    total_energy: float

class UserHabitsAnalysis(BaseModel):
    time_distribution: Dict[int, int]  # 小时 -> 使用次数
    most_used_devices: Dict[str, int]  # 设备名称 -> 使用次数
    total_usage_time: float
    average_daily_usage: float

class EnergyConsumptionAnalysis(BaseModel):
    total_consumption: float
    daily_average: float
    device_consumption: Dict[str, float]  # 设备名称 -> 能耗

class DeviceHealthAnalysis(BaseModel):
    device_id: int
    device_name: str
    status: str
    last_usage: Optional[datetime]
    last_maintenance: Optional[datetime]
    health_score: float

class SecurityEvent(BaseModel):
    event_id: int
    event_type: str
    timestamp: datetime
    description: str
    severity: str
    device_id: Optional[int]
    location: Optional[str]

class SecurityAnalysis(BaseModel):
    total_events: int
    event_types: Dict[str, int]  # 事件类型 -> 数量
    recent_events: List[SecurityEvent]  # 最近的事件列表
    risk_level: str  # 风险等级

class DeviceTimeAnalysis(BaseModel):
    hourly_usage: Dict[int, int]  # 小时 -> 使用次数
    device_type_usage: Dict[str, Dict[int, int]]  # 设备类型 -> {小时 -> 使用次数}

class DeviceCorrelation(BaseModel):
    device1: str
    device2: str
    time1: datetime
    time2: datetime
    time_diff: float

class DeviceCorrelationAnalysis(BaseModel):
    correlations: List[DeviceCorrelation]
    correlation_count: Dict[str, int]  # "设备1-设备2" -> 关联次数

class DeviceStats(BaseModel):
    type: str
    usage_count: int
    total_energy: float
    usage_per_sqm: float
    energy_per_sqm: float

class HouseStats(BaseModel):
    house_id: int
    house_name: str
    area: float
    device_stats: List[DeviceStats]

class HouseAreaImpactAnalysis(BaseModel):
    house_stats: List[HouseStats]

class AnalyticsData(BaseModel):
    """分析数据模型"""
    timestamp: datetime
    value: float
    metric: str
    device_id: Optional[int] = None
    house_id: Optional[int] = None

class AnalyticsResponse(BaseModel):
    """分析响应模型"""
    data: List[AnalyticsData]
    summary: Dict[str, Any]
    metadata: Dict[str, Any] 