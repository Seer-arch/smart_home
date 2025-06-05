from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import House
from app.schemas.house import HouseCreate, HouseUpdate

class CRUDHouse(CRUDBase[House, HouseCreate, HouseUpdate]):
    """房屋 CRUD 操作"""
    
    def get_by_owner(self, db: Session, *, owner_id: int) -> List[House]:
        """获取指定用户的所有房屋"""
        return db.query(self.model).filter(self.model.user_id == owner_id).all()

crud_house = CRUDHouse(House) 