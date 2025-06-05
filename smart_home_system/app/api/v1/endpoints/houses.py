from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app import crud, models
from app.api import deps
from app.schemas.house import (
    House,
    HouseCreate,
    HouseUpdate,
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[House])
def read_houses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    获取当前用户的所有房屋列表
    """
    try:
        houses = crud.crud_house.get_by_owner(db, owner_id=current_user.id)
        return houses
    except Exception as e:
        logger.error(f"获取房屋列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取房屋列表失败"
        )

@router.post("/", response_model=House)
def create_house(
    *,
    db: Session = Depends(deps.get_db),
    house_in: HouseCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    创建新房屋
    """
    try:
        # 设置房屋所有者
        house_data = house_in.dict()
        house_data["user_id"] = current_user.id
        house = crud.crud_house.create(db=db, obj_in=house_data)
        return house
    except Exception as e:
        logger.error(f"创建房屋失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建房屋失败: {str(e)}"
        )

@router.get("/{house_id}", response_model=House)
def read_house(
    *,
    db: Session = Depends(deps.get_db),
    house_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    通过ID获取房屋信息
    """
    try:
        house = crud.crud_house.get(db=db, id=house_id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="房屋不存在"
            )
        # 验证权限
        if house.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限访问此房屋"
            )
        return house
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取房屋信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取房屋信息失败"
        )

@router.put("/{house_id}", response_model=House)
def update_house(
    *,
    db: Session = Depends(deps.get_db),
    house_id: int,
    house_in: HouseUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    更新房屋信息
    """
    try:
        house = crud.crud_house.get(db=db, id=house_id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="房屋不存在"
            )
        # 验证权限
        if house.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限修改此房屋"
            )
        house = crud.crud_house.update(db=db, db_obj=house, obj_in=house_in)
        return house
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新房屋失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新房屋失败"
        )

@router.delete("/{house_id}", response_model=House)
def delete_house(
    *,
    db: Session = Depends(deps.get_db),
    house_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    删除房屋
    """
    try:
        house = crud.crud_house.get(db=db, id=house_id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="房屋不存在"
            )
        # 验证权限
        if house.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限删除此房屋"
            )
        house = crud.crud_house.remove(db=db, id=house_id)
        return house
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除房屋失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除房屋失败"
        ) 