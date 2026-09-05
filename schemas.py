from pydantic import BaseModel
from datetime import datetime

class TicketCreate(BaseModel):
    title: str
    description: str

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    created_at: datetime
    similar_tickets: list = []

    class Config:
        from_attributes = True