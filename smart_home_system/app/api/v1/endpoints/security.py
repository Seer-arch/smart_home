from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.security import SecurityEventCreate, SecurityEventUpdate, SecurityEvent
from app.crud.crud_security import crud_security
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=SecurityEvent)
def create_security_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: SecurityEventCreate
) -> SecurityEvent:
    """
    创建新的安全事件记录
    """
    try:
        return crud_security.create(db=db, obj_in=event_in)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建安全事件失败: {str(e)}"
        )

@router.get("/", response_model=List[SecurityEvent])
def get_security_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    house_id: Optional[int] = None,
    device_id: Optional[int] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[SecurityEvent]:
    """
    获取安全事件列表，支持多种过滤条件
    """
    try:
        return crud_security.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            house_id=house_id,
            device_id=device_id,
            event_type=event_type,
            severity=severity,
            status=status,
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取安全事件列表失败: {str(e)}"
        )

@router.get("/{event_id}", response_model=SecurityEvent)
def get_security_event(
    event_id: int,
    db: Session = Depends(deps.get_db)
) -> SecurityEvent:
    """
    获取单个安全事件详情
    """
    try:
        event = crud_security.get(db=db, id=event_id)
        if not event:
            raise HTTPException(
                status_code=404,
                detail="安全事件不存在"
            )
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取安全事件详情失败: {str(e)}"
        )

@router.put("/{event_id}", response_model=SecurityEvent)
def update_security_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    event_in: SecurityEventUpdate
) -> SecurityEvent:
    """
    更新安全事件信息
    """
    try:
        event = crud_security.get(db=db, id=event_id)
        if not event:
            raise HTTPException(
                status_code=404,
                detail="安全事件不存在"
            )
        return crud_security.update(db=db, db_obj=event, obj_in=event_in)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新安全事件失败: {str(e)}"
        )

@router.delete("/{event_id}")
def delete_security_event(
    event_id: int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    删除安全事件
    """
    try:
        event = crud_security.get(db=db, id=event_id)
        if not event:
            raise HTTPException(
                status_code=404,
                detail="安全事件不存在"
            )
        crud_security.remove(db=db, id=event_id)
        return {"message": "安全事件已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除安全事件失败: {str(e)}"
        ) 