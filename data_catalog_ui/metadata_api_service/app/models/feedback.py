from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    dataset_id: str
    column_name: str
    suggested_glossary: str
    notes: Optional[str] = None
    current_glossary: Optional[str] = None # Optional, can be fetched by backend

class FeedbackInDB(FeedbackCreate):
    id: str
    status: str = "Pending Review"
    submitted_by: str = "System" # Placeholder, get from auth in real app
    submitted_date: datetime = datetime.now()