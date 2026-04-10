from sqlalchemy.orm import Session
from langchain_core.tools import StructuredTool
from models.problembox_models import Ticket, TicketTimeline, TicketPriority, TicketStatus
from pydantic import BaseModel, Field
from datetime import datetime

class ReportIssueInput(BaseModel):
    title: str = Field(description="A short, descriptive title of the issue (e.g. 'Leaking faucet')")
    description: str = Field(description="Detailed explanation of the problem")
    location: str = Field(description="Campus location (e.g. 'Room 302', 'Library Lawn')")
    category: str = Field(description="Category of the problem (e.g. 'Plumbing', 'Electrical', 'Furniture')")
    priority: str = Field(description="Priority level: 'Low', 'Medium', 'High', 'Critical'", default="Medium")

class TicketStatusInput(BaseModel):
    ticket_id: str = Field(description="The ticket ID to check progress for (e.g. 'TKT-1234')")

def report_campus_issue(db: Session, user_id: str, title: str, description: str, location: str, category: str, priority: str) -> str:
    """Creates a formal maintenance or infrastructure ticket in the ProblemBox system."""
    try:
        # Map string priority to Enum
        prio_enum = getattr(TicketPriority, priority, TicketPriority.Medium)
        
        new_ticket = Ticket(
            title=title,
            description=description,
            location=location,
            category_id=category,
            priority=prio_enum,
            reporter_id=user_id,
            status=TicketStatus.Raised
        )
        db.add(new_ticket)
        db.flush() # Get the ID
        
        # Add initial timeline event
        timeline_event = TicketTimeline(
            ticket_id=new_ticket.id,
            step_name="Reported via UAssist",
            update_text=f"Issue logged by AI assistant. {description}",
            is_completed=True
        )
        db.add(timeline_event)
        db.commit()
        
        return f"SUCCESS: Ticket {new_ticket.id} has been raised. The infrastructure team has been notified. Location: {location}."
    except Exception as e:
        db.rollback()
        return f"ERROR: Failed to create ticket: {str(e)}"

def check_ticket_progress(db: Session, ticket_id: str) -> str:
    """Fetches the latest status and timeline updates for a specific ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        return f"No ticket found with ID '{ticket_id}'."
        
    timeline = db.query(TicketTimeline).filter(TicketTimeline.ticket_id == ticket_id).order_by(TicketTimeline.timestamp.desc()).all()
    
    status_msg = f"Ticket {ticket_id} Status: {ticket.status}\nLocation: {ticket.location}\nTimeline:\n"
    for step in timeline:
        time_str = step.timestamp.strftime("%Y-%m-%d %H:%M") if step.timestamp else "N/A"
        status_msg += f"- [{time_str}] {step.step_name}: {step.update_text or ''}\n"
    return status_msg

def make_problembox_tools(db: Session, user_id: str) -> list:
    def _report(title: str, description: str, location: str, category: str, priority: str = "Medium"):
        return report_campus_issue(db, user_id, title, description, location, category, priority)
        
    def _status(ticket_id: str):
        return check_ticket_progress(db, ticket_id)
        
    return [
        StructuredTool.from_function(
            func=_report,
            name="report_campus_issue",
            description="Use this when a student wants to report a problem, maintenance issue, or broken infrastructure on campus.",
            args_schema=ReportIssueInput
        ),
        StructuredTool.from_function(
            func=_status,
            name="check_ticket_status",
            description="Use this to check the current progress or status of an existing ticket using its ID.",
            args_schema=TicketStatusInput
        )
    ]
