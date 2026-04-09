from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from utils.session_maker import make_db_session
from models.shopperz_models import RetailInventory, MarketListing
from schemas.shopperz_schemas import RetailResponse, MarketResponse, RetailOut, MarketOut, RetailIn, MarketIn
from utils.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/api/shopperz", tags=["Shopperz"])

@router.get("/retail", response_model=RetailResponse, dependencies=[Depends(get_current_user)])
def get_retail_inventory(db: Session = Depends(make_db_session)):
    items = db.query(RetailInventory).all()
    return RetailResponse(success=True, data=items)

@router.get("/market", response_model=MarketResponse, dependencies=[Depends(get_current_user)])
def get_market_listings(db: Session = Depends(make_db_session)):
    # Eager load the nested seller object to instantly hydrate standard JSON structure securely
    listings = db.query(MarketListing).options(joinedload(MarketListing.seller)).all()
    return MarketResponse(success=True, data=listings)

@router.post("/retail", response_model=RetailOut, dependencies=[Depends(get_current_admin)])
def create_retail_item(payload: RetailIn, db: Session = Depends(make_db_session)):
    new_retail = RetailInventory(**payload.model_dump(by_alias=False))
    db.add(new_retail)
    db.commit()
    db.refresh(new_retail)
    return new_retail

@router.post("/market", response_model=MarketOut)
def create_market_listing(payload: MarketIn, db: Session = Depends(make_db_session), current_user = Depends(get_current_user)):
    new_market = MarketListing(seller_id=current_user.id, **payload.model_dump(by_alias=False))
    db.add(new_market)
    db.commit()
    db.refresh(new_market)
    
    # We must eagerly load the nested seller relationship so the response_model parser
    # correctly finds the mapped current_user when outputting the nested SellerOut JSON construct.
    query_hydrated = db.query(MarketListing).options(joinedload(MarketListing.seller)).filter_by(id=new_market.id).first()
    return query_hydrated
