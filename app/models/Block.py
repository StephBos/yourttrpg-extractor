from pydantic import BaseModel

class Block(BaseModel):
    title: str
    content: str
    page_start: int
    page_end: int
    