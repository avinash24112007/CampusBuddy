from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from utils.session_maker import make_db_session
from models.problembox_models import Ticket, TicketTimeline
from schemas.problembox_schemas import TicketResponse, TicketOut, TicketIn, ReporterOut, TimelineOut
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/problembox", tags=["ProblemBox"], dependencies=[Depends(get_current_user)])

def serialize_ticket(t: Ticket) -> dict:
    reporter_data = {
        "name": "Anonymous Issue" if t.is_anonymous else getattr(t.reporter, "name", "Student"),
        "anonymous": t.is_anonymous
    }
    
    timeline_data = []
    if t.timeline:
        for step in t.timeline:
            time_str = step.timestamp.strftime("%I:%M %p") if step.timestamp else ""
            timeline_data.append({
                "id": str(step.id),
                "step": step.step_name,
                "time": time_str,
                "active": not step.is_completed, 
                "completed": step.is_completed
            })
            
    return {
        "id": t.id,
        "title": t.title,
        "location": t.location,
        "description": t.description,
        "category": t.category_id,
        "priority": t.priority,
        "status": t.status,
        "reporter": reporter_data,
        "upvotes": t.upvotes,
        "hasResolvedViewed": t.has_resolved_viewed,
        "media": t.media,
        "timeline": timeline_data
    }

@router.get("/tickets", response_model=TicketResponse)
def get_tickets(db: Session = Depends(make_db_session)):
    tickets = db.query(Ticket).options(
        joinedload(Ticket.reporter),
        joinedload(Ticket.timeline)
    ).all()
    
    output = [TicketOut(**serialize_ticket(t)) for t in tickets]
    return TicketResponse(success=True, data=output)

@router.post("/tickets", response_model=TicketOut)
def create_ticket(payload: TicketIn, db: Session = Depends(make_db_session), current_user = Depends(get_current_user)):
    new_ticket = Ticket(
        title=payload.title,
        description=payload.description,
        location=payload.location,
        category_id=payload.category,
        priority=payload.priority,
        is_anonymous=payload.anonymous,
        media=payload.media,
        reporter_id=current_user.id
    )
    
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    timeline_event = TicketTimeline(
        ticket_id=new_ticket.id,
        step_name="Reported",
        update_text="Ticket successfully uploaded directly to the Campus Infrastructure team.",
        is_completed=True
    )
    db.add(timeline_event)
    db.commit()
    
    hydrated = db.query(Ticket).options(
        joinedload(Ticket.reporter),
        joinedload(Ticket.timeline)
    ).filter_by(id=new_ticket.id).first()
    
    return TicketOut(**serialize_ticket(hydrated))
