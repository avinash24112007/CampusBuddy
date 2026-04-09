from pydantic import BaseModel, Field
from typing import Optional

class FoodSearchInput(BaseModel):
    keyword: Optional[str] = Field(None, description="General search keywords from the user like 'spicy', 'dosa', 'combos'.")
    category: Optional[str] = Field(None, description="Food category, like 'South Indian', 'Beverages', 'Snacks'.")
    canteen: Optional[str] = Field(None, description="The name of the canteen to search in, like 'Container'.")
    max_price: Optional[int] = Field(None, description="The maximum price in rupees the student is willing to pay.")
    min_price: Optional[int] = Field(None, description="The minimum price in rupees.")
    only_available: bool = Field(True, description="Whether to filter only currently available/in-stock items. Default generally is true.")
class ArenaEventSearchInput(BaseModel):
    keyword: Optional[str] = Field(None, description="General keyword matching event title, description, organizer, or tags (e.g. 'hackathon', 'AI').")
    mode: Optional[str] = Field(None, description="Event mode filter. Values should be 'Online', 'Offline', or 'Hybrid'.")
    status: Optional[str] = Field(None, description="Event status filter. Values usually 'Upcoming', 'Ongoing', or 'Completed'.")
    is_paid: Optional[bool] = Field(None, description="True for paid events, False for strictly free events, None for either.")
    max_fee: Optional[float] = Field(None, description="Maximum registration fee the student is willing to pay.")
    only_available: bool = Field(True, description="Default True. Filters out events where filled capacity has reached total capacity.")
    tags: Optional[list[str]] = Field(None, description="List of category tags to filter by. Example: ['coding', 'music'].")

class MyRegistrationsInput(BaseModel):
    user_id: str = Field(..., description="The UUID of the logged-in student initiating the request.")
    status: Optional[str] = Field(None, description="Filter by status, valid options usually 'Registered', 'Cancelled', or 'Attended'.")

class FindTeammatesInput(BaseModel):
    event_id: str = Field(..., description="The UUID of the specific event to find teammates for.")
    tier: Optional[str] = Field(None, description="Skill tier filter. Usually 'Beginner', 'Intermediate', or 'Expert'.")
    status: Optional[str] = Field("Pending", description="Filter teammate request states. Defaults to 'Pending'.")

class EventDetailsInput(BaseModel):
    event_id: Optional[str] = Field(None, description="The precise UUID of the event if already discovered.")
    title_keyword: Optional[str] = Field(None, description="Alternative lookup using partial event title matches if the ID isn't provided.")

class ArenaChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str
