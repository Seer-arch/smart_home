from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import json

from app import crud, models, schemas
from app.api import deps

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/me",
    response_model=schemas.User,
    summary="Get current user information",
    description="Get detailed information about the currently logged-in user",
    response_description="Detailed information about the current user"
)
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get detailed information about the currently logged-in user
    
    Returns:
    - Detailed information about the current user
    """
    try:
        # Ensure preferences is a dictionary type
        if isinstance(current_user.preferences, str):
            try:
                current_user.preferences = json.loads(current_user.preferences)
            except json.JSONDecodeError:
                current_user.preferences = {}
        return current_user
    except Exception as e:
        logger.error(f"Failed to get user information: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.put(
    "/me",
    response_model=schemas.User,
    summary="Update current user information",
    description="Update personal information for the currently logged-in user",
    response_description="Updated user information"
)
async def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_in: schemas.UserUpdate
) -> Any:
    """
    Update personal information for the currently logged-in user
    
    - **full_name**: User's full name
    - **phone_number**: Phone number
    - **preferences**: User preferences
    
    Returns:
    - Updated user information
    """
    try:
        user = crud.crud_user.get(db, id=current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )
        
        user = crud.crud_user.update(db, db_obj=user, obj_in=user_in)
        return user
    except Exception as e:
        logger.error(f"Failed to update user information: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information"
        )

@router.get(
    "/{user_id}",
    response_model=schemas.User,
    summary="Get user information by ID",
    description="Get detailed information about a user by their ID",
    response_description="Detailed information about the specified user"
)
async def read_user(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get detailed information about a user by their ID
    
    - **user_id**: User ID
    
    Returns:
    - Detailed information about the specified user
    """
    try:
        user = crud.crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )
        return user
    except Exception as e:
        logger.error(f"Failed to get user information: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.get(
    "/",
    response_model=List[schemas.User],
    summary="Get user list",
    description="Get a list of all users in the system",
    response_description="User list"
)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get a list of all users in the system
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    
    Returns:
    - User list
    """
    try:
        users = crud.crud_user.get_multi(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error(f"Failed to get user list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user list"
        )

@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Delete a user by ID",
    response_description="Delete result"
)
async def delete_user(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Delete a user
    """
    user = crud.crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete current user"
        )
    user = crud.crud_user.remove(db, id=user_id)
    return {"message": "User has been deleted"} 