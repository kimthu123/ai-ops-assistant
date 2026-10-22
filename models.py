from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone

DATABASE_URL = "sqlite:///./data/tickets.db"

engine = create_engine(DATABASE_URL, connect_args= {"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    severity = Column(String, default="unclassified")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_to = Column(Integer, index=True, nullable=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()