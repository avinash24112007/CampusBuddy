from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from utils.session_maker import make_db_session
from models.arena_models import ArenaEvent
from schemas.arena_schemas import ArenaEventResponse, ArenaEventOut, ArenaEventIn, TimelineOut, CapacityOut
from utils.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/api/arena", tags=["Arena"])

def serialize_event(ev: ArenaEvent) -> dict:
    now = datetime.now(timezone.utc)
    
    # Calculate startsIn dynamically
    if ev.start_time.replace(tzinfo=timezone.utc) <= now:
        starts_in = "Now"
    else:
        delta = ev.start_time.replace(tzinfo=timezone.utc) - now
        days = delta.days
        hours = delta.seconds // 3600
        if days > 0:
            starts_in = f"{days}d {hours}h"
        else:
            starts_in = f"{hours}h"

    return {
        "id": ev.id,
        "title": ev.title,
        "organizer": ev.organizer,
        "coverImage": ev.cover_image_url,
        "date": ev.start_time.strftime("%Y-%m-%d"),
        "location": ev.location,
        "tags": ev.tags if ev.tags else [],
        "status": ev.status,
        "mode": ev.mode,
        "description": ev.description,
        "fee": float(ev.fee),
        "isPaid": ev.is_paid,
        "prizePot": ev.prize_pot,
        "timeline": {
            "startsIn": starts_in,
            "deadline": ev.deadline.strftime("%Y-%m-%d")
        },
        "capacity": {
            "total": ev.total_capacity,
            "filled": ev.filled_capacity
        },
        "isFeatured": ev.is_featured
    }

@router.get("/events", response_model=ArenaEventResponse, dependencies=[Depends(get_current_user)])
def get_events(db: Session = Depends(make_db_session)):
    events = db.query(ArenaEvent).all()
    output = [ArenaEventOut(**serialize_event(ev)) for ev in events]
    return ArenaEventResponse(success=True, data=output)

@router.post("/events", response_model=ArenaEventOut, dependencies=[Depends(get_current_admin)])
def create_event(payload: ArenaEventIn, db: Session = Depends(make_db_session)):
    new_event = ArenaEvent(
        title=payload.title,
        organizer=payload.organizer,
        description=payload.description,
        cover_image_url=payload.coverImage,
        mode=payload.mode,
        start_time=payload.startTime,
        deadline=payload.deadline,
        is_paid=payload.isPaid,
        fee=payload.fee,
        max_team_size=payload.maxTeamSize,
        location=payload.location,
        prize_pot=payload.prizePot,
        is_featured=payload.isFeatured,
        total_capacity=payload.totalCapacity,
        tags=payload.tags
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return ArenaEventOut(**serialize_event(new_event))
