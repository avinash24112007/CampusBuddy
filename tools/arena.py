from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone
from langchain_core.tools import StructuredTool
from schemas.uassist_schemas import (
    ArenaEventSearchInput, MyRegistrationsInput, 
    FindTeammatesInput, EventDetailsInput
)
from models.arena_models import ArenaEvent, ArenaRegistration, ArenaTeamSync

def search_arena_events(
    db: Session,
    keyword: str | None = None,
    mode: str | None = None,
    status: str | None = None,
    is_paid: bool | None = None,
    max_fee: float | None = None,
    only_available: bool = True,
    tags: list[str] | None = None
) -> str:
    query = db.query(ArenaEvent)

    if only_available:
        query = query.filter(ArenaEvent.filled_capacity < ArenaEvent.total_capacity)

    if keyword:
        query = query.filter(
            or_(
                ArenaEvent.title.ilike(f"%{keyword}%"),
                ArenaEvent.description.ilike(f"%{keyword}%"),
                ArenaEvent.organizer.ilike(f"%{keyword}%"),
                ArenaEvent.tags.overlap([keyword])
            )
        )

    if mode:
        query = query.filter(ArenaEvent.mode.ilike(f"%{mode}%"))
    
    if status:
        query = query.filter(ArenaEvent.status.ilike(f"%{status}%"))

    if is_paid is not None:
        query = query.filter(ArenaEvent.is_paid == is_paid)
    
    if max_fee is not None:
        query = query.filter(ArenaEvent.fee <= max_fee)

    if tags:
        query = query.filter(ArenaEvent.tags.overlap(tags))

    results = query.limit(6).all()

    if not results:
        return "No events found matching your criteria."

    lines = [f"Found {len(results)} event(s):\n"]
    for idx, e in enumerate(results, 1):
        fee_str = f"₹{e.fee}" if e.is_paid and e.fee > 0 else "Free"
        spots_left = e.total_capacity - e.filled_capacity
        tags_str = ", ".join(e.tags) if e.tags else "None"
        start_str = e.start_time.strftime("%Y-%m-%d %H:%M") if e.start_time else "TBA"
        
        lines.append(
            f"{idx}. {e.title} (by {e.organizer})\n"
            f"   Mode   : {e.mode}\n"
            f"   Status : {e.status}\n"
            f"   Date   : {start_str}\n"
            f"   Fee    : {fee_str}\n"
            f"   Spots  : {spots_left} left\n"
            f"   Tags   : {tags_str}\n"
        )
    return "\n".join(lines)


def check_my_registrations(
    db: Session,
    user_id: str,
    status: str | None = None
) -> str:
    query = db.query(ArenaRegistration, ArenaEvent).join(ArenaEvent, ArenaRegistration.event_id == ArenaEvent.id)
    query = query.filter(ArenaRegistration.user_id == user_id)
    
    if status:
        query = query.filter(ArenaRegistration.status.ilike(f"%{status}%"))

    results = query.order_by(ArenaRegistration.registered_at.desc()).limit(10).all()

    if not results:
        return "You have no event registrations matching this criteria."

    lines = [f"Showing your registrations ({len(results)} found):\n"]
    for reg, event in results:
        team_str = f" (Team: {reg.team_name})" if reg.team_name else ""
        date_str = event.start_time.strftime("%Y-%m-%d %H:%M") if event.start_time else "TBA"
        reg_date_str = reg.registered_at.strftime("%Y-%m-%d") if reg.registered_at else "Unknown"

        lines.append(
            f"👉 {event.title} - {event.mode}\n"
            f"   When   : {date_str}\n"
            f"   Status : {reg.status}{team_str}\n"
            f"   Booked : {reg_date_str}\n"
        )
    return "\n".join(lines)


def find_teammates(
    db: Session,
    event_id: str,
    tier: str | None = None,
    status: str | None = "Pending"
) -> str:
    # First get the event context
    event = db.query(ArenaEvent).filter(ArenaEvent.id == event_id).first()
    if not event:
        return "Error: Event not found."
    
    spots_open = event.max_team_size - event.filled_capacity

    query = db.query(ArenaTeamSync).filter(ArenaTeamSync.event_id == event_id)
    if tier:
        query = query.filter(ArenaTeamSync.tier.ilike(f"%{tier}%"))
    if status:
        query = query.filter(ArenaTeamSync.status.ilike(f"%{status}%"))

    results = query.limit(10).all()

    lines = [f"Teammate finder for '{event.title}'"]
    lines.append(f"Event capacity info: {spots_open} spots still open across teams (Max team size: {event.max_team_size})\n")
    
    if not results:
        lines.append("No active teammate requests found for this filter.")
        return "\n".join(lines)

    lines.append(f"Found {len(results)} sync requests:\n")
    for row in results:
        sync_date = row.created_at.strftime("%Y-%m-%d") if row.created_at else "Unknown"
        lines.append(
            f"👤 Req: {row.requester_id} | Recip: {row.recipient_id}\n"
            f"   Tier   : {row.tier}\n"
            f"   Status : {row.status}\n"
            f"   Posted : {sync_date}\n"
        )
    return "\n".join(lines)


def get_event_details(
    db: Session,
    event_id: str | None = None,
    title_keyword: str | None = None
) -> str:
    if not event_id and not title_keyword:
        return "Error: Must provide either event_id or title_keyword to find details."

    query = db.query(ArenaEvent)
    if event_id:
        query = query.filter(ArenaEvent.id == event_id)
    else:
        query = query.filter(ArenaEvent.title.ilike(f"%{title_keyword}%"))

    event = query.first()
    if not event:
        return "Event not found."

    spots_remaining = event.total_capacity - event.filled_capacity
    
    now_utc = datetime.now(timezone.utc)
    # Check if deadline is tz-aware, convert securely
    try:
        if event.deadline and event.deadline.tzinfo is None:
            dl = event.deadline.replace(tzinfo=timezone.utc)
        else:
            dl = event.deadline
        registration_open = dl > now_utc if dl else False
    except:
        registration_open = False

    fee_str = f"₹{event.fee}" if event.is_paid else "Free"
    tags_str = ", ".join(event.tags) if event.tags else "None"
    cover_str = event.cover_image_url if event.cover_image_url else "No cover image"

    lines = [
        f"**{event.title}**",
        f"Organizer: {event.organizer}",
        f"Mode: {event.mode} | Status: {event.status}",
        f"Tags: {tags_str}",
        f"Image: {cover_str}",
        f"Description: {event.description}",
        f"\n-- Registration Info --",
        f"Takes place: {event.start_time}",
        f"Deadline: {event.deadline}",
        f"Registration Open: {'✅ Yes' if registration_open else '❌ Closed'}",
        f"Fee: {fee_str}",
        f"Max Team Size: {event.max_team_size}",
        f"Capacity: {event.filled_capacity}/{event.total_capacity} filled (Spots remaining: {spots_remaining})"
    ]
    return "\n".join(lines)


def make_arena_tools(db: Session) -> list:
    
    def _search_events(
        keyword: str | None = None, mode: str | None = None, status: str | None = None, 
        is_paid: bool | None = None, max_fee: float | None = None, 
        only_available: bool = True, tags: list[str] | None = None
    ):
        return search_arena_events(db, keyword, mode, status, is_paid, max_fee, only_available, tags)

    def _my_registrations(user_id: str, status: str | None = None):
        return check_my_registrations(db, user_id, status)

    def _teammates(event_id: str, tier: str | None = None, status: str | None = "Pending"):
        return find_teammates(db, event_id, tier, status)

    def _event_details(event_id: str | None = None, title_keyword: str | None = None):
        return get_event_details(db, event_id, title_keyword)

    return [
        StructuredTool.from_function(
            func=_search_events,
            name="search_arena_events",
            description="Use to discover or filter arena events (e.g. hackathons, contests).",
            args_schema=ArenaEventSearchInput
        ),
        StructuredTool.from_function(
            func=_my_registrations,
            name="check_my_registrations",
            description="Use to see events the student has already registered for.",
            args_schema=MyRegistrationsInput
        ),
        StructuredTool.from_function(
            func=_teammates,
            name="find_teammates",
            description="Use to find teammates or team sync requests for a specific event.",
            args_schema=FindTeammatesInput
        ),
        StructuredTool.from_function(
            func=_event_details,
            name="get_event_details",
            description="Use to fetch full details including deadlines and capacity for a specific event.",
            args_schema=EventDetailsInput
        )
    ]
