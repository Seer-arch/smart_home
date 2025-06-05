from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class VisualizationData(BaseModel):
    """可视化数据模型"""
    timestamp: datetime
    value: float
    category: str
    device_id: Optional[int] = None
    house_id: Optional[int] = None

class VisualizationResponse(BaseModel):
    """可视化响应模型"""
    data: List[VisualizationData]
    chart_type: str
    options: Dict[str, Any]

class DeviceUsageVisualization(BaseModel):
    """设备使用情况可视化数据模型"""
    labels: List[str]  # 设备名称列表
    usage_data: List[int]  # 使用次数列表
    duration_data: List[float]  # 平均使用时长列表（分钟）
    energy_data: List[float]  # 总能耗列表（kWh）

class DeviceTimeVisualization(BaseModel):
    """设备使用时间段可视化数据模型"""
    hours: List[int]  # 小时列表（0-23）
    hourly_usage: List[int]  # 每小时使用次数
    device_type_usage: Dict[str, Dict[int, int]]  # 每种设备类型的小时使用统计

class DeviceCorrelationVisualization(BaseModel):
    """设备关联性可视化数据模型"""
    correlations: List[Dict[str, Any]]  # 设备关联记录列表
    correlation_count: Dict[str, int]  # 设备关联次数统计

class DeviceStats(BaseModel):
    """设备统计数据模型"""
    type: str  # 设备类型
    usage_count: int  # 使用次数
    total_energy: float  # 总能耗
    usage_per_sqm: float  # 每平方米使用频率
    energy_per_sqm: float  # 每平方米能耗

class HouseStats(BaseModel):
    """房屋统计数据模型"""
    house_id: int  # 房屋ID
    house_name: str  # 房屋名称
    area: float  # 房屋面积
    device_stats: List[DeviceStats]  # 设备统计列表

class HouseAreaVisualization(BaseModel):
    """房屋面积影响可视化数据模型"""
    house_stats: List[HouseStats]  # 房屋统计列表 