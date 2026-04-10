from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from utils.session_maker import make_db_session
from models.shopperz_models import RetailInventory, MarketListing, RetailOrder, RetailOrderItem, PrintQueue
from schemas.shopperz_schemas import (
    RetailResponse, MarketResponse, RetailOut, MarketOut, RetailIn, MarketIn,
    RetailOrderIn, MarketReserveIn, PrintJobIn, PrintJobResponse
)
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
    new_retail = RetailInventory(
        name=payload.name,
        category=payload.category,
        price=payload.price,
        image_url=payload.image,
        stock_level=payload.stock,
        is_duo_sync=payload.isDuoSync,
        duo_price=payload.duoPrice,
        bulk_min=payload.bulkMin,
        bulk_price=payload.bulkPrice
    )
    db.add(new_retail)
    db.commit()
    db.refresh(new_retail)
    return new_retail

@router.post("/market", response_model=MarketOut)
def create_market_listing(payload: MarketIn, db: Session = Depends(make_db_session), current_user = Depends(get_current_user)):
    new_market = MarketListing(
        seller_id=current_user.id,
        title=payload.title,
        condition=payload.condition,
        price=payload.price,
        original_price=payload.originalPrice,
        image_url=payload.image
    )
    db.add(new_market)
    db.commit()
    db.refresh(new_market)
    
    # We must eagerly load the nested seller relationship so the response_model parser
    # correctly finds the mapped current_user when outputting the nested SellerOut JSON construct.
    query_hydrated = db.query(MarketListing).options(joinedload(MarketListing.seller)).filter_by(id=new_market.id).first()
    return query_hydrated


@router.post("/retail/order")
def place_retail_order(payload: RetailOrderIn, db: Session = Depends(make_db_session), current_user = Depends(get_current_user)):
    # 1. Total & Security check using backend calculation
    total_calculated = 0
    items_to_persist = []
    
    for item in payload.items:
        prod = db.query(RetailInventory).get(item.id)
        if not prod:
             raise HTTPException(status_code=404, detail=f"Product {item.id} not found")
             
        if prod.stock_level < item.quantity:
            raise HTTPException(status_code=400, detail=f"Item {prod.name} is out of stock")
            
        # Bulk Deal Pricing Logic
        unit_price = prod.price
        if prod.bulk_min and item.quantity >= prod.bulk_min:
            unit_price = prod.bulk_price
            
        subtotal = float(unit_price) * item.quantity
        total_calculated += subtotal
        
        items_to_persist.append({
            "product": prod,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "subtotal": subtotal
        })

    # 2. Wallet check
    if current_user.balance < total_calculated:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
    
    # 3. Deduct balance
    current_user.balance -= total_calculated
    
    # 4. Create Order
    new_order = RetailOrder(user_id=current_user.id, total_amount=total_calculated)
    db.add(new_order)
    db.flush()
    
    for entry in items_to_persist:
        prod = entry["product"]
        prod.stock_level -= entry["quantity"]
        # Increment product-specific revenue
        prod.total_sales = float(prod.total_sales or 0) + entry["subtotal"]
        
        order_item = RetailOrderItem(
            order_id=new_order.id,
            product_id=prod.id,
            quantity=entry["quantity"],
            price_at_time=entry["unit_price"]
        )
        db.add(order_item)
        
    db.commit()
    return {"success": True, "order_id": new_order.id, "total": total_calculated}


@router.patch("/market/{listing_id}/reserve")
def reserve_market_item(listing_id: int, payload: MarketReserveIn, db: Session = Depends(make_db_session), current_user = Depends(get_current_user)):
    listing = db.query(MarketListing).filter_by(id=listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing.status != 'Available':
         raise HTTPException(status_code=400, detail="Item already reserved or sold")
         
    listing.status = 'Reserved'
    listing.reservation_expiry = datetime.utcnow() + timedelta(hours=2)
    db.commit()
    return {"success": True}


@router.post("/print")
def submit_print_job(payload: PrintJobIn, db: Session = Depends(make_db_session), current_user = Depends(get_current_user)):
    if current_user.balance < payload.cost:
        raise HTTPException(status_code=400, detail="Insufficient balance for printing")
    
    current_user.balance -= payload.cost
    
    new_job = PrintQueue(
        user_id=current_user.id,
        file_metadata={"name": payload.name, "pages": payload.pages, "type": payload.type},
        cost_total=payload.cost
    )
    db.add(new_job)
    db.commit()
    return {"success": True}


@router.get("/print", response_model=PrintJobResponse)
def get_user_print_jobs(db: Session = Depends(make_db_session), current_user = Depends(get_current_user)):
    jobs = db.query(PrintQueue).filter_by(user_id=current_user.id).order_by(PrintQueue.id.desc()).all()
    return PrintJobResponse(success=True, data=jobs)
