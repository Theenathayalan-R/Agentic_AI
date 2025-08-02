from typing import List
from app.models.feedback import FeedbackCreate, FeedbackInDB
import uuid
from datetime import datetime

_feedback_db: List[FeedbackInDB] = [] # In-memory "database" for demonstration

def create_feedback(feedback_in: FeedbackCreate) -> FeedbackInDB:
    feedback_entry = FeedbackInDB(
        id=str(uuid.uuid4()),
        submitted_date=datetime.now(),
        **feedback_in.model_dump()
    )
    _feedback_db.append(feedback_entry)
    return feedback_entry

def get_all_feedback() -> List[FeedbackInDB]:
    return _feedback_db[:]