from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from utils.session_maker import make_db_session
from models.shopperz_models import RetailInventory, MarketListing
from schemas.shopperz_schemas import RetailResponse, MarketResponse
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/shopperz", tags=["Shopperz"], dependencies=[Depends(get_current_user)])

@router.get("/retail", response_model=RetailResponse)
def get_retail_inventory(db: Session = Depends(make_db_session)):
    items = db.query(RetailInventory).all()
    return RetailResponse(success=True, data=items)

@router.get("/market", response_model=MarketResponse)
def get_market_listings(db: Session = Depends(make_db_session)):
    # Eager load the nested seller object to instantly hydrate standard JSON structure securely
    listings = db.query(MarketListing).options(joinedload(MarketListing.seller)).all()
    return MarketResponse(success=True, data=listings)
