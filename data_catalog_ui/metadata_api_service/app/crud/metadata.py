from typing import List
from app.models.metadata import ColumnMetadata, DatasetMetadata
from app.core.trino import TrinoClient
from app.crud.dataset import get_dataset_by_id
from app.crud.domain import get_all_domains

trino_client = TrinoClient()

def get_full_metadata_for_dataset(dataset_id: str) -> DatasetMetadata:
    dataset = get_dataset_by_id(dataset_id)
    if not dataset:
        return None

    all_domains = get_all_domains()
    domain_name = next((d.domain_name for d in all_domains if d.domain_id == dataset.domain_id), "Unknown")

    columns_meta = trino_client.get_column_metadata(dataset_id)
    
    return DatasetMetadata(
        dataset_id=dataset.dataset_id,
        dataset_name=dataset.table_name,
        domain_name=domain_name,
        description=dataset.description,
        columns=columns_meta
    )