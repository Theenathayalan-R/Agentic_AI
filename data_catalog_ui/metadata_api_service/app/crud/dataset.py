from typing import List, Optional
from app.models.dataset import Dataset
from app.core.trino import TrinoClient

trino_client = TrinoClient()

def get_datasets_by_domain(domain_id: str) -> List[Dataset]:
    datasets_df = trino_client.get_datasets_for_domain(domain_id)
    return [Dataset(**row) for row in datasets_df.to_dict(orient='records')]

def get_dataset_by_id(dataset_id: str) -> Optional[Dataset]:
    dataset_info = trino_client.get_dataset_info(dataset_id)
    if dataset_info:
        return Dataset(**dataset_info)
    return None