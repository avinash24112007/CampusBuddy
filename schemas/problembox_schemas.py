from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID

# For POST parsing
class TicketIn(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    category: Optional[str] = None
    priority: str = "Medium"
    anonymous: bool = False
    media: List[str] = Field(default_factory=list)

# For GET structuring
class ReporterOut(BaseModel):
    name: str
    anonymous: bool

class TimelineOut(BaseModel):
    id: str
    step: str
    time: str
    active: bool
    completed: bool

class TicketOut(BaseModel):
    id: str
    title: str
    location: Optional[str] = None
    description: str
    category: Optional[str] = None
    priority: str
    status: str
    reporter: ReporterOut
    upvotes: int = 0
    hasResolvedViewed: bool = False
    media: List[str] = Field(default_factory=list)
    timeline: List[TimelineOut] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

class TicketResponse(BaseModel):
    success: bool = True
    data: List[TicketOut]
