from fastapi import APIRouter, HTTPException
from typing import List
from app.models.dataset import Dataset
from app.models.metadata import DatasetMetadata
from app.crud import dataset as crud_dataset
from app.crud import metadata as crud_metadata

router = APIRouter()

@router.get("/by-domain/{domain_id}", response_model=List[Dataset])
def read_datasets_by_domain(domain_id: str):
    datasets = crud_dataset.get_datasets_by_domain(domain_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="No datasets found for this domain")
    return datasets

@router.get("/{dataset_id}/metadata", response_model=DatasetMetadata)
def read_dataset_metadata(dataset_id: str):
    full_metadata = crud_metadata.get_full_metadata_for_dataset(dataset_id)
    if not full_metadata:
        raise HTTPException(status_code=404, detail="Dataset metadata not found")
    return full_metadata