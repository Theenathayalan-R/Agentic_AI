from pydantic import BaseModel

class Dataset(BaseModel):
    dataset_id: str
    domain_id: str
    table_name: str
    description: str