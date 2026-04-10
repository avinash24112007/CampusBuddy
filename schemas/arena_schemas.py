from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# --- POST Input ---
class ArenaEventIn(BaseModel):
    title: str
    organizer: str
    description: str
    coverImage: Optional[str] = Field(alias="coverImage", default=None)
    mode: str
    startTime: datetime = Field(alias="startTime")
    deadline: datetime
    isPaid: bool = Field(alias="isPaid", default=False)
    fee: float = 0.0
    maxTeamSize: int = Field(alias="maxTeamSize", default=1)
    location: Optional[str] = None
    prizePot: Optional[str] = Field(alias="prizePot", default=None)
    isFeatured: bool = Field(alias="isFeatured", default=False)
    totalCapacity: int = Field(alias="totalCapacity")
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

# --- GET Output ---
class TimelineOut(BaseModel):
    startsIn: str
    deadline: str

class CapacityOut(BaseModel):
    total: int
    filled: int

class ArenaEventOut(BaseModel):
    id: str
    title: str
    organizer: str
    coverImage: Optional[str] = None
    date: str
    location: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    status: str
    mode: str
    description: str
    fee: float
    isPaid: bool
    prizePot: Optional[str] = None
    timeline: TimelineOut
    capacity: CapacityOut
    isFeatured: bool

class ArenaEventResponse(BaseModel):
    success: bool = True
    data: List[ArenaEventOut]


# --- RSVP & REGISTRATION ---
class ArenaRegistrationIn(BaseModel):
    eventId: str = Field(alias="eventId")
    teamName: Optional[str] = Field(alias="teamName", default=None)

    model_config = ConfigDict(populate_by_name=True)

class ArenaRegistrationOut(BaseModel):
    id: int
    eventId: str = Field(alias="eventId", validation_alias="event_id")
    userId: str = Field(alias="userId", validation_alias="user_id")
    teamName: Optional[str] = Field(alias="teamName", validation_alias="team_name", default=None)
    status: str
    registeredAt: datetime = Field(alias="registeredAt", validation_alias="registered_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ArenaRegistrationResponse(BaseModel):
    success: bool = True
    data: List[ArenaRegistrationOut]


# --- TEAM SYNC ---
class ArenaTeamSyncIn(BaseModel):
    eventId: str = Field(alias="eventId")
    recipientId: str = Field(alias="recipientId")
    tier: str

    model_config = ConfigDict(populate_by_name=True)

class ArenaTeamSyncOut(BaseModel):
    id: int
    eventId: str = Field(alias="eventId", validation_alias="event_id")
    requesterId: str = Field(alias="requesterId", validation_alias="requester_id")
    recipientId: str = Field(alias="recipientId", validation_alias="recipient_id")
    tier: str
    status: str
    createdAt: datetime = Field(alias="createdAt", validation_alias="created_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ArenaTeamSyncUpdate(BaseModel):
    status: str # 'Accepted', 'Declined'

class ArenaTeamSyncResponse(BaseModel):
    success: bool = True
    data: List[ArenaTeamSyncOut]
