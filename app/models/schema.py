from pydantic import BaseModel

class Query(BaseModel):
    destination: str
    user: str = "default"