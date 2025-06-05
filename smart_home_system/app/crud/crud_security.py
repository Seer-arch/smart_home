from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import SecurityEvent
from app.schemas.security import SecurityEventCreate, SecurityEventUpdate
from datetime import datetime

class CRUDSecurity:
    def create(self, db: Session, *, obj_in: SecurityEventCreate) -> SecurityEvent:
        """创建安全事件"""
        db_obj = SecurityEvent(
            house_id=obj_in.house_id,
            device_id=obj_in.device_id,
            event_type=obj_in.event_type,
            event_time=obj_in.event_time,
            description=obj_in.description,
            severity=obj_in.severity,
            status=obj_in.status,
            event_metadata=obj_in.event_metadata
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[SecurityEvent]:
        """获取单个安全事件"""
        return db.query(SecurityEvent).filter(SecurityEvent.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
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
        """获取安全事件列表"""
        query = db.query(SecurityEvent)
        
        if house_id:
            query = query.filter(SecurityEvent.house_id == house_id)
        if device_id:
            query = query.filter(SecurityEvent.device_id == device_id)
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type)
        if severity:
            query = query.filter(SecurityEvent.severity == severity)
        if status:
            query = query.filter(SecurityEvent.status == status)
        if start_time:
            query = query.filter(SecurityEvent.event_time >= start_time)
        if end_time:
            query = query.filter(SecurityEvent.event_time <= end_time)
        
        return query.order_by(SecurityEvent.event_time.desc()).offset(skip).limit(limit).all()

    def update(
        self,
        db: Session,
        *,
        db_obj: SecurityEvent,
        obj_in: SecurityEventUpdate
    ) -> SecurityEvent:
        """更新安全事件"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> SecurityEvent:
        """删除安全事件"""
        obj = db.query(SecurityEvent).get(id)
        db.delete(obj)
        db.commit()
        return obj

crud_security = CRUDSecurity() 