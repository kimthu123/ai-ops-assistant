from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from models import Base, engine, get_db, Ticket
from schemas import TicketCreate, TicketResponse

import os
from anthropic import Anthropic
from rag import add_ticket_to_index, find_similar_tickets

Base.metadata.create_all(bind=engine)

app = FastAPI()   #test

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def classify_severity(title: str, description: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=10,
        messages=[
            {
                "role": "user",
                "content": f"Classify the severity of this IT ticket as exactly one word (low, medium, high, or critical). Title: {title}. Description: {description}. Respond with only the severity word."
            }
        ]
    )
    return message.content[0].text.strip().lower()

@app.post("/tickets", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    severity = classify_severity(ticket.title, ticket.description)
    new_ticket = Ticket(title=ticket.title, description=ticket.description, severity=severity)
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    similar_results = find_similar_tickets(ticket.title, ticket.description)
    similar_list = []
    for ticket_id, document, distance in zip(
        similar_results["ids"][0],
        similar_results["documents"][0],
        similar_results["distances"][0]
    ):
        similar_list.append({
            "ticket_id": int(ticket_id),
            "content": document,
            "similarity_distance": distance
        })
    add_ticket_to_index(new_ticket.id, new_ticket.title, new_ticket.description)

    new_ticket.similar_tickets = similar_list
    return new_ticket

@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).all()

@app.get("/tickets/{ticket_id}")
def find_one_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.put("/tickets/{ticket_id}")
def update_tickets(ticket_id: int, ticket: TicketCreate, db: Session = Depends(get_db)):
    existing_ticket= db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if existing_ticket is None:
        raise HTTPException(status_code=404)
    existing_ticket.title = ticket.title
    existing_ticket.description = ticket.description
    existing_ticket.severity = classify_severity(ticket.title, ticket.description)
    db.commit()
    db.refresh(existing_ticket)
    return existing_ticket

@app.get("/tickets/search/similar")
def search_similar_tickets(title: str, description: str):
    results = find_similar_tickets(title, description)
    
    similar = [] #hihi
    for ticket_id, document, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["distances"][0]
    ):
        similar.append({
            "ticket_id": int(ticket_id),
            "content": document,
            "similarity_distance": distance
        })
    
    return similar

@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    deleted_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if deleted_ticket is None:
       raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(deleted_ticket)
    db.commit()
    return {"message": "Ticket deleted", "ticket_id": ticket_id}





