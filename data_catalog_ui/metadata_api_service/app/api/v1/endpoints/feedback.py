from fastapi import APIRouter, status, Body
from typing import List
from app.models.feedback import FeedbackCreate, FeedbackInDB
from app.crud import feedback as crud_feedback

router = APIRouter()

@router.post("/", response_model=FeedbackInDB, status_code=status.HTTP_201_CREATED)
def create_new_feedback(feedback: FeedbackCreate):
    return crud_feedback.create_feedback(feedback)

@router.get("/", response_model=List[FeedbackInDB])
def read_all_feedback():
    return crud_feedback.get_all_feedback()