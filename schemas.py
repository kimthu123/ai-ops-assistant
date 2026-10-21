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

class SeverityCount(BaseModel):
    severity: str
    count: int

class SeverityAnalytics(BaseModel):
    total: int
    by_severity: list [SeverityCount] 

class DailyCount(BaseModel):
    date: str
    num_tickets: int

class DailyAnalytics(BaseModel):
    total: int
    by_dailycount: list[DailyCount]


