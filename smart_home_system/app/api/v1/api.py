from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    houses,
    rooms,
    devices,
    device_usage,
    device_maintenance,
    security,
    analytics,
    visualization,
    feedback
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(houses.router, prefix="/houses", tags=["房屋"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["房间"])
api_router.include_router(devices.router, prefix="/devices", tags=["设备"])
api_router.include_router(device_usage.router, prefix="/device-usage", tags=["设备使用"])
api_router.include_router(device_maintenance.router, prefix="/device-maintenance", tags=["设备维护"])
api_router.include_router(security.router, prefix="/security", tags=["安全"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["数据分析"])
api_router.include_router(visualization.router, prefix="/visualization", tags=["数据可视化"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["用户反馈"]) 