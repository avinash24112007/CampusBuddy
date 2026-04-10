from fastapi import APIRouter, Depends, Query, Request, Response, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from utils.session_maker import make_db_session
from models.caffenity_models import Canteen, MenuItem, Order, OrderItem
from schemas.caffenity_schemas import MenuResponse, CanteenResponse, MenuItemOut, CanteenOut, CanteenIn, MenuItemIn, OrderResponse, OrderIn, OrderOut
from utils.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/api/caffenity", tags=["Caffenity"])

@router.get("/canteens", response_model=CanteenResponse, dependencies=[Depends(get_current_user)])
def get_canteens(db: Session = Depends(make_db_session)):
    canteens = db.query(Canteen).all()
    return CanteenResponse(success=True, data=canteens)

@router.get("/menu", response_model=MenuResponse, dependencies=[Depends(get_current_user)])
def get_menu(
    canteen_id: Optional[str] = Query(None, description="Filter menu by specific canteen ID"),
    db: Session = Depends(make_db_session)
):
    query = db.query(MenuItem)
    if canteen_id:
        query = query.filter(MenuItem.canteen_id == canteen_id)
        
    items = query.all()
    
    # Process array data explicitly enforcing unified JSON contract rule
    for item in items:
        if item.tags is None:
            item.tags = []
            
    return MenuResponse(success=True, data=items)

@router.post("/canteens", response_model=CanteenOut, dependencies=[Depends(get_current_admin)])
def create_canteen(payload: CanteenIn, db: Session = Depends(make_db_session)):
    new_canteen = Canteen(**payload.model_dump())
    db.add(new_canteen)
    db.commit()
    db.refresh(new_canteen)
    return new_canteen

@router.post("/menu", response_model=MenuItemOut, dependencies=[Depends(get_current_admin)])
def create_menu_item(payload: MenuItemIn, db: Session = Depends(make_db_session)):
    new_item = MenuItem(**payload.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/orders", response_model=OrderResponse, dependencies=[Depends(get_current_user)])
def get_orders(
    canteen_id: Optional[str] = Query(None),
    db: Session = Depends(make_db_session)
):
    query = db.query(Order)
    if canteen_id:
        query = query.filter(Order.canteen_id == canteen_id)
        
    orders = query.all()
    return OrderResponse(success=True, data=orders)


@router.post("/order", response_model=OrderOut)
def create_order(
    payload: OrderIn, 
    db: Session = Depends(make_db_session),
    current_user = Depends(get_current_user)
):
    # 1. Fetch menu items to verify existence and get prices
    menu_item_ids = [item.id for item in payload.items]
    db_items = db.query(MenuItem).filter(MenuItem.id.in_(menu_item_ids)).all()
    item_map = {item.id: item for item in db_items}
    
    if len(db_items) != len(menu_item_ids):
        missing = set(menu_item_ids) - set(item_map.keys())
        raise HTTPException(status_code=400, detail=f"Invalid menu items: {missing}")
        
    # 2. Calculate total amount
    total_amount = 0
    for item_in in payload.items:
        db_item = item_map[item_in.id]
        total_amount += float(db_item.price) * item_in.quantity
        
    # 3. Handle Wallet Payment
    if payload.paymentMethod == "CAMPUS Wallet":
        if current_user.balance < total_amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        
        current_user.balance -= int(total_amount) # balance is Integer
        db.add(current_user)
        
    # 4. Create Order
    new_order = Order(
        canteen_id=payload.canteenId,
        student_name=current_user.name,
        total_amount=total_amount,
        scheduled_time=payload.scheduledTime,
        payment_method=payload.paymentMethod,
        special_note=payload.specialNote,
        status="Placed"
    )
    db.add(new_order)
    db.flush() # Get new_order.id
    
    # 5. Create Order Items
    for item_in in payload.items:
        db_item = item_map[item_in.id]
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item_in.id,
            quantity=item_in.quantity,
            price_at_time_of_order=db_item.price
        )
        db.add(order_item)
        
    db.commit()
    db.refresh(new_order)
    
    return new_order

