from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app import crud, models, schemas
from app.api import deps
from app.schemas.device import Device, DeviceCreate, DeviceUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Device])
def read_devices(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取设备列表
    """
    try:
        devices = crud.crud_device.get_multi(db, skip=skip, limit=limit)
        return devices
    except Exception as e:
        logger.error(f"获取设备列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取设备列表失败"
        )

@router.post("/", response_model=Device)
def create_device(
    *,
    db: Session = Depends(deps.get_db),
    device_in: DeviceCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建设备
    """
    try:
        # 验证房间是否存在
        room = db.query(models.Room).filter(models.Room.id == device_in.room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="房间不存在"
            )
        
        # 验证用户是否有权限访问该房间
        house = db.query(models.House).filter(models.House.id == room.house_id).first()
        if not house or house.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限在此房间创建设备"
            )
        
        # 创建设备
        device = crud.crud_device.create(db, obj_in=device_in)
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建设备失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建设备失败: {str(e)}"
        )

@router.get("/{device_id}", response_model=Device)
def read_device(
    *,
    db: Session = Depends(deps.get_db),
    device_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取设备详情
    """
    try:
        device = crud.crud_device.get(db, id=device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="设备不存在"
            )
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取设备详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取设备详情失败"
        )

@router.put("/{device_id}", response_model=Device)
def update_device(
    *,
    db: Session = Depends(deps.get_db),
    device_id: int,
    device_in: DeviceUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新设备
    """
    try:
        device = crud.crud_device.get(db, id=device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="设备不存在"
            )
        device = crud.crud_device.update(db, db_obj=device, obj_in=device_in)
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新设备失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新设备失败"
        )

@router.delete("/{device_id}", response_model=Device)
def delete_device(
    *,
    db: Session = Depends(deps.get_db),
    device_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    删除设备
    """
    try:
        device = crud.crud_device.get(db, id=device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="设备不存在"
            )
        device = crud.crud_device.remove(db, id=device_id)
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除设备失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除设备失败"
        ) 