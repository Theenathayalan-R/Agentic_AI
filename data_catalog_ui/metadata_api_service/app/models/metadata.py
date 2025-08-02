from pydantic import BaseModel
from typing import List

class ColumnMetadata(BaseModel):
    column_name: str
    data_type: str
    technical_description: str
    business_glossary: str

class DatasetMetadata(BaseModel):
    dataset_id: str
    dataset_name: str
    domain_name: str
    description: str
    columns: List[ColumnMetadata]