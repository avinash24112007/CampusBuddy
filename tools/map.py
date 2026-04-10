from sqlalchemy.orm import Session
from sqlalchemy import or_
from langchain_core.tools import StructuredTool
from models.map_models import Building, Room
from pydantic import BaseModel, Field

class MapSearchInput(BaseModel):
    query: str = Field(description="The name of the building or room to find (e.g. 'Main Building', 'L-201')")

def search_campus_locations(db: Session, query: str) -> str:
    """Finds buildings or rooms on the campus map and returns coordinates."""
    # Search Buildings
    buildings = db.query(Building).filter(
        or_(
            Building.name.ilike(f"%{query}%"),
            Building.description.ilike(f"%{query}%")
        )
    ).limit(3).all()
    
    # Search Rooms
    rooms = db.query(Room).filter(
        or_(
            Room.name.ilike(f"%{query}%"),
            Room.building_id.ilike(f"%{query}%")
        )
    ).limit(3).all()
    
    if not buildings and not rooms:
        return f"No locations found for '{query}' on the campus map."
        
    lines = [f"I found some matches on the map for '{query}':\n"]
    for b in buildings:
        lines.append(f"🏢 Building: {b.name}\n   Location: {b.lat}, {b.lng}\n   About: {b.description or 'No data'}")
        
    for r in rooms:
        lines.append(f"🚪 Room: {r.name}\n   Building ID: {r.building_id}")
        
    return "\n".join(lines)

def make_map_tools(db: Session) -> list:
    def _search(query: str):
        return search_campus_locations(db, query)
        
    return [
        StructuredTool.from_function(
            func=_search,
            name="search_campus_map",
            description="Use this when a student asks for the location of a building, room, or facility on campus.",
            args_schema=MapSearchInput
        )
    ]
