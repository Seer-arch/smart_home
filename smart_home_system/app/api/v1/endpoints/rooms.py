from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app import crud, models
from app.api import deps
from app.schemas.room import Room, RoomCreate, RoomUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Room])
def read_rooms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    获取当前用户的所有房间列表
    """
    try:
        # 获取用户的所有房屋
        houses = crud.crud_house.get_by_owner(db, owner_id=current_user.id)
        house_ids = [house.id for house in houses]
        
        # 获取这些房屋的所有房间
        rooms = db.query(models.Room).filter(models.Room.house_id.in_(house_ids)).all()
        return rooms
    except Exception as e:
        logger.error(f"获取房间列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取房间列表失败"
        )

@router.post("/", response_model=Room)
def create_room(
    *,
    db: Session = Depends(deps.get_db),
    room_in: RoomCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    创建新房间
    """
    try:
        # 验证房屋是否存在且属于当前用户
        house = crud.crud_house.get(db=db, id=room_in.house_id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="房屋不存在"
            )
        if house.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限在此房屋创建房间"
            )
        
        # 创建房间
        room = crud.crud_room.create(db=db, obj_in=room_in)
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建房间失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建房间失败: {str(e)}"
        )

@router.get("/{room_id}", response_model=Room)
def read_room(
    *,
    db: Session = Depends(deps.get_db),
    room_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    通过ID获取房间信息
    """
    try:
        room = crud.crud_room.get(db=db, id=room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="房间不存在"
            )
        
        # 验证权限
        house = crud.crud_house.get(db=db, id=room.house_id)
        if not house or house.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限访问此房间"
            )
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取房间信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取房间信息失败"
        )

@router.put("/{room_id}", response_model=Room)
def update_room(
    *,
    db: Session = Depends(deps.get_db),
    room_id: int,
    room_in: RoomUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    更新房间信息
    """
    try:
        room = crud.crud_room.get(db=db, id=room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="房间不存在"
            )
        
        # 验证权限
        house = crud.crud_house.get(db=db, id=room.house_id)
        if not house or house.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限修改此房间"
            )
        
        room = crud.crud_room.update(db=db, db_obj=room, obj_in=room_in)
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新房间失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新房间失败"
        )

@router.delete("/{room_id}", response_model=Room)
def delete_room(
    *,
    db: Session = Depends(deps.get_db),
    room_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    删除房间
    """
    try:
        room = crud.crud_room.get(db=db, id=room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="房间不存在"
            )
        
        # 验证权限
        house = crud.crud_house.get(db=db, id=room.house_id)
        if not house or house.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限删除此房间"
            )
        
        room = crud.crud_room.remove(db=db, id=room_id)
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除房间失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除房间失败"
        ) 