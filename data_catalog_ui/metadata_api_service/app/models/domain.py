from pydantic import BaseModel

class Domain(BaseModel):
    domain_id: str
    domain_name: str
    description: str