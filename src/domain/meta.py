from pydantic import BaseModel

class Meta(BaseModel):
    name: str
    note: str
    images: list[str]