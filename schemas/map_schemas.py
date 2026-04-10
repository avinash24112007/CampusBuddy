from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class BuildingOut(BaseModel):
    id: str
    name: str
    shortCode: str = Field(validation_alias="short_code")
    floors: List[int] = []
    x: float = 0.0
    z: float = 0.0
    w: float = 0.0
    d: float = 0.0
    status: str = "available"
    facilities: List[str] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RoomOut(BaseModel):
    id: str
    name: str
    floor: str
    capacity: int = 0
    status: str = "Available"
    bookedBy: Optional[str] = Field(validation_alias="booked_by", default=None)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LiveMarkerOut(BaseModel):
    id: str
    type: str
    buildingId: str = Field(validation_alias="building_id")
    pulseColor: str = Field(validation_alias="pulse_color", default="Blue")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MapDataResponse(BaseModel):
    """Full map payload matching the frontend's expected JSON shape."""
    success: bool = True
    buildings: List[BuildingOut]
    rooms: dict[str, List[RoomOut]] = {}       # keyed by building_id
    markers: List[LiveMarkerOut] = []
