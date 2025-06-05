from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Device
from app.schemas.device import DeviceCreate, DeviceUpdate
from datetime import datetime

class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    """设备 CRUD 操作"""
    
    def get_by_house(self, db: Session, *, house_id: int) -> List[Device]:
        """获取指定房屋的所有设备"""
        return db.query(self.model).filter(self.model.house_id == house_id).all()
    
    def create(self, db: Session, *, obj_in: DeviceCreate) -> Device:
        """创建设备，处理日期转换"""
        obj_in_data = obj_in.dict()
        # 设置创建和更新时间
        obj_in_data["created_at"] = datetime.utcnow()
        obj_in_data["updated_at"] = datetime.utcnow()
        # 创建数据库对象
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_device = CRUDDevice(Device) 