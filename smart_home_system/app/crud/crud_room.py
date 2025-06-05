from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Room
from app.schemas.room import RoomCreate, RoomUpdate

class CRUDRoom(CRUDBase[Room, RoomCreate, RoomUpdate]):
    """房间 CRUD 操作"""
    
    def get_by_house(self, db: Session, *, house_id: int) -> List[Room]:
        """获取指定房屋的所有房间"""
        return db.query(self.model).filter(self.model.house_id == house_id).all()

crud_room = CRUDRoom(Room) 