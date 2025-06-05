from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import User
from app.services.visualization import VisualizationService

router = APIRouter()

@router.get("/area-impact")
async def get_area_impact_analysis(
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Dict:
    """获取房屋面积影响分析数据"""
    visualization_service = VisualizationService(db)
    return visualization_service.get_area_impact_data()

@router.get("/device/{device_id}/usage-trend")
async def get_device_usage_trend(
    device_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Dict:
    """获取设备使用趋势数据"""
    visualization_service = VisualizationService(db)
    return visualization_service.get_device_usage_trend_data(device_id)

@router.get("/device/{device_id}/time-distribution")
async def get_device_time_distribution(
    device_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Dict:
    """获取设备使用时间分布数据"""
    visualization_service = VisualizationService(db)
    return visualization_service.get_device_time_distribution_data(device_id)

@router.get("/device/{device_id}/scenario-analysis")
async def get_device_scenario_analysis(
    device_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Dict:
    """获取设备使用场景分析数据"""
    visualization_service = VisualizationService(db)
    return visualization_service.get_device_usage_by_scenario_data(device_id)

@router.get("/device/{device_id}/environmental-impact")
async def get_device_environmental_impact(
    device_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Dict:
    """获取环境因素影响分析数据"""
    visualization_service = VisualizationService(db)
    return visualization_service.get_environmental_impact_data(device_id)

@router.get("/device/correlation")
async def get_device_correlation(
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Dict:
    """获取设备关联使用分析数据"""
    visualization_service = VisualizationService(db)
    return visualization_service.get_device_correlation_data()

@router.get("/automation-analysis")
async def get_automation_analysis(
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Dict:
    """获取自动化使用分析数据"""
    visualization_service = VisualizationService(db)
    return visualization_service.get_automation_analysis_data() 