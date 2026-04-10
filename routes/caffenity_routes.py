from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session
from typing import Optional

from utils.session_maker import make_db_session
from models.caffenity_models import Canteen, MenuItem, Order
from schemas.caffenity_schemas import MenuResponse, CanteenResponse, MenuItemOut, CanteenOut, CanteenIn, MenuItemIn, OrderResponse
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

