from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict

from utils.session_maker import make_db_session
from models.map_models import Building, Room, LiveMarker
from schemas.map_schemas import MapDataResponse, BuildingOut, RoomOut, LiveMarkerOut
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/map", tags=["Map"])


@router.get("/data", response_model=MapDataResponse, dependencies=[Depends(get_current_user)])
def get_map_data(db: Session = Depends(make_db_session)):
    """Returns the full map payload the 3D frontend engine expects."""
    
    # Buildings
    buildings = db.query(Building).all()
    
    # Rooms grouped by building_id
    all_rooms = db.query(Room).all()
    rooms_by_building: dict[str, list] = defaultdict(list)
    for room in all_rooms:
        rooms_by_building[room.building_id].append(room)
    
    # Live markers
    markers = db.query(LiveMarker).all()
    
    return MapDataResponse(
        success=True,
        buildings=buildings,
        rooms={bid: rooms for bid, rooms in rooms_by_building.items()},
        markers=markers
    )
