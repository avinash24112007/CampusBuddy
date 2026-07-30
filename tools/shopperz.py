from sqlalchemy.orm import Session
from sqlalchemy import or_
from langchain_core.tools import StructuredTool
from models.shopperz_models import RetailInventory, MarketListing
from pydantic import BaseModel, Field
from utils.session_maker import get_db_session
class ShopperzSearchInput(BaseModel):
    query: str = Field(description="The search term for products or listings (e.g. 'notebook', 'hoodie')")

def search_shopperz_retail(db: Session, query: str) -> str:
    """Search for official items in the Campus Store."""
    results = db.query(RetailInventory).filter(
        or_(
            RetailInventory.name.ilike(f"%{query}%"),
            RetailInventory.category.ilike(f"%{query}%")
        )
    ).limit(5).all()
    
    if not results:
        return f"No store products found for '{query}'."
        
    lines = [f"Found {len(results)} product(s) in the Store:\n"]
    for p in results:
        lines.append(f"- {p.name} ({p.category}): ₹{p.price}. Stock: {p.stock_level}")
    return "\n".join(lines)

def search_shopperz_market(db: Session, query: str) -> str:
    """Search for student-listed items in the Marketplace."""
    results = db.query(MarketListing).filter(
        or_(
            MarketListing.title.ilike(f"%{query}%"),
            MarketListing.condition.ilike(f"%{query}%")
        ),
        MarketListing.status == 'Available'
    ).limit(5).all()
    
    if not results:
        return f"No marketplace listings found for '{query}'."
        
    lines = [f"Found {len(results)} listing(s) in the Marketplace:\n"]
    for l in results:
        lines.append(f"- {l.title} (Condition: {l.condition}): ₹{l.price}")
    return "\n".join(lines)

def make_shopperz_tools() -> list:
    with get_db_session() as db:
        def _search_retail(query: str):
            return search_shopperz_retail(db, query)
    with get_db_session() as db:

        def _search_market(query: str):
            return search_shopperz_market(db, query)
        
    return [
        StructuredTool.from_function(
            func=_search_retail,
            name="search_campus_store",
            description="Use this to find official products like apparel, stationery, and equipment in the KU Store.",
            args_schema=ShopperzSearchInput
        ),
        StructuredTool.from_function(
            func=_search_market,
            name="search_student_market",
            description="Use this to find used items, books, or gear listed by other students in the marketplace.",
            args_schema=ShopperzSearchInput
        )
    ]
