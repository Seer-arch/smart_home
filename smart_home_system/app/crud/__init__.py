from app.crud.crud_user import crud_user
from app.crud.crud_device import crud_device
from app.crud.crud_house import crud_house
from app.crud.crud_room import crud_room

# 导出所有 CRUD 对象
__all__ = [
    "crud_user",
    "crud_device",
    "crud_house",
    "crud_room",
]

# 为了向后兼容，添加 user 属性
user = crud_user 