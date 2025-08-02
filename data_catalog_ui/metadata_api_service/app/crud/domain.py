from typing import List
from app.models.domain import Domain
from app.core.trino import TrinoClient

trino_client = TrinoClient()

def get_all_domains() -> List[Domain]:
    domains_df = trino_client.get_domains()
    return [Domain(**row) for row in domains_df.to_dict(orient='records')]