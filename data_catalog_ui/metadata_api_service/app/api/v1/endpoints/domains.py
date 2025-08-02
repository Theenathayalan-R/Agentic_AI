from fastapi import APIRouter
from typing import List
from app.models.domain import Domain
from app.crud import domain as crud_domain

router = APIRouter()

@router.get("/", response_model=List[Domain])
def read_domains():
    return crud_domain.get_all_domains()