from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_user, get_db
from app.models.models import User, UserFeedback, FeedbackStatus
from app.schemas.schemas import (
    UserFeedbackCreate,
    UserFeedbackUpdate,
    UserFeedback as UserFeedbackSchema,
    UserFeedbackResponse
)

router = APIRouter()

@router.post("/", response_model=UserFeedbackSchema)
async def create_feedback(
    feedback: UserFeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建用户反馈"""
    db_feedback = UserFeedback(
        user_id=current_user.id,
        content=feedback.content,
        feedback_type=feedback.feedback_type,
        priority=feedback.priority
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/", response_model=List[UserFeedbackSchema])
async def get_feedbacks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有反馈"""
    return db.query(UserFeedback).filter(UserFeedback.user_id == current_user.id).all()

@router.get("/admin/all", response_model=List[UserFeedbackResponse])
async def get_all_feedbacks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status: FeedbackStatus = None,
    feedback_type: str = None
):
    """管理员获取所有反馈"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    query = db.query(UserFeedback)
    
    if status:
        query = query.filter(UserFeedback.status == status)
    if feedback_type:
        query = query.filter(UserFeedback.feedback_type == feedback_type)
    
    feedbacks = query.all()
    return [
        UserFeedbackResponse(
            **feedback.__dict__,
            user_email=feedback.user.email,
            user_full_name=feedback.user.full_name
        )
        for feedback in feedbacks
    ]

@router.get("/{feedback_id}", response_model=UserFeedbackSchema)
async def get_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取特定反馈的详细信息"""
    feedback = db.query(UserFeedback).filter(
        UserFeedback.id == feedback_id,
        UserFeedback.user_id == current_user.id
    ).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    return feedback

@router.put("/{feedback_id}", response_model=UserFeedbackSchema)
async def update_feedback(
    feedback_id: int,
    feedback_update: UserFeedbackUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新反馈信息"""
    feedback = db.query(UserFeedback).filter(
        UserFeedback.id == feedback_id,
        UserFeedback.user_id == current_user.id
    ).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    # 普通用户只能更新内容和类型
    update_data = feedback_update.dict(exclude_unset=True)
    if not current_user.is_superuser:
        update_data = {
            k: v for k, v in update_data.items()
            if k in ['content', 'feedback_type']
        }
    
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    db.commit()
    db.refresh(feedback)
    return feedback

@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除反馈"""
    feedback = db.query(UserFeedback).filter(
        UserFeedback.id == feedback_id,
        UserFeedback.user_id == current_user.id
    ).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    db.delete(feedback)
    db.commit()
    return None

@router.put("/admin/{feedback_id}/respond", response_model=UserFeedbackResponse)
async def admin_respond_to_feedback(
    feedback_id: int,
    response: UserFeedbackUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """管理员回复反馈"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    feedback = db.query(UserFeedback).filter(UserFeedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    update_data = response.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    db.commit()
    db.refresh(feedback)
    
    return UserFeedbackResponse(
        **feedback.__dict__,
        user_email=feedback.user.email,
        user_full_name=feedback.user.full_name
    ) 