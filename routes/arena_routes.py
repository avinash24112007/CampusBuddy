from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from utils.session_maker import make_db_session
from models.arena_models import ArenaEvent, ArenaRegistration, ArenaTeamSync
from schemas.arena_schemas import (
    ArenaEventResponse, ArenaEventOut, ArenaEventIn, TimelineOut, CapacityOut,
    ArenaRegistrationIn, ArenaRegistrationOut, ArenaRegistrationResponse,
    ArenaTeamSyncIn, ArenaTeamSyncOut, ArenaTeamSyncUpdate, ArenaTeamSyncResponse
)
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


# --- RSVP / REGISTRATION ---

@router.post("/rsvp", response_model=ArenaRegistrationOut)
def rsvp_to_event(
    payload: ArenaRegistrationIn,
    db: Session = Depends(make_db_session),
    current_user = Depends(get_current_user)
):
    # Check if event exists
    event = db.query(ArenaEvent).filter(ArenaEvent.id == payload.eventId).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Check if already registered
    existing = db.query(ArenaRegistration).filter(
        ArenaRegistration.event_id == payload.eventId,
        ArenaRegistration.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this event")
        
    # Check capacity
    if event.filled_capacity >= event.total_capacity:
        raise HTTPException(status_code=400, detail="Event is full")
        
    # Create registration
    new_reg = ArenaRegistration(
        event_id=payload.eventId,
        user_id=current_user.id,
        team_name=payload.teamName,
        status="Confirmed"
    )
    
    # Increment capacity
    event.filled_capacity += 1
    
    db.add(new_reg)
    db.add(event)
    db.commit()
    db.refresh(new_reg)
    
    return new_reg


@router.get("/registrations", response_model=ArenaRegistrationResponse)
def get_user_registrations(
    db: Session = Depends(make_db_session),
    current_user = Depends(get_current_user)
):
    regs = db.query(ArenaRegistration).filter(ArenaRegistration.user_id == current_user.id).all()
    return ArenaRegistrationResponse(success=True, data=regs)


# --- TEAM SYNC ---

@router.post("/team-sync", response_model=ArenaTeamSyncOut)
def send_team_sync_request(
    payload: ArenaTeamSyncIn,
    db: Session = Depends(make_db_session),
    current_user = Depends(get_current_user)
):
    # Check if event exists
    event = db.query(ArenaEvent).filter(ArenaEvent.id == payload.eventId).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Create sync request
    new_sync = ArenaTeamSync(
        event_id=payload.eventId,
        requester_id=current_user.id,
        recipient_id=payload.recipientId,
        tier=payload.tier,
        status="Pending"
    )
    
    db.add(new_sync)
    db.commit()
    db.refresh(new_sync)
    
    return new_sync


@router.get("/team-sync", response_model=ArenaTeamSyncResponse)
def get_team_sync_requests(
    db: Session = Depends(make_db_session),
    current_user = Depends(get_current_user)
):
    # Get requests where user is either requester or recipient
    syncs = db.query(ArenaTeamSync).filter(
        (ArenaTeamSync.requester_id == current_user.id) | 
        (ArenaTeamSync.recipient_id == current_user.id)
    ).all()
    return ArenaTeamSyncResponse(success=True, data=syncs)


@router.patch("/team-sync/{sync_id}", response_model=ArenaTeamSyncOut)
def update_team_sync_status(
    sync_id: int,
    payload: ArenaTeamSyncUpdate,
    db: Session = Depends(make_db_session),
    current_user = Depends(get_current_user)
):
    sync = db.query(ArenaTeamSync).filter(ArenaTeamSync.id == sync_id).first()
    if not sync:
        raise HTTPException(status_code=404, detail="Sync request not found")
        
    if sync.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can update the status")
        
    sync.status = payload.status
    db.commit()
    db.refresh(sync)
    
    # If accepted, we could automatically RSVP the recipient if not already done, 
    # but for now we'll let the UI handle it or keep it simple.
    
    return sync
