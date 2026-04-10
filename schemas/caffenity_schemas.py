from pydantic import BaseModel, Field
from typing import Optional, List

class CanteenIn(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    is_active: bool = True

class CanteenOut(BaseModel):
    id: int
    name: str
    location: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class MenuItemIn(BaseModel):
    canteen_id: int
    name: str
    description: Optional[str] = None
    category: str
    price: float
    prep_time: Optional[str] = None
    image_url: Optional[str] = None
    calories: Optional[int] = None
    is_veg: bool = True
    is_special: bool = False
    in_stock: bool = True
    tags: List[str] = Field(default_factory=list)

class MenuItemOut(BaseModel):
    id: int
    canteen_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: str
    price: float
    prep_time: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = 0.0
    calories: Optional[int] = None
    is_veg: bool = True
    is_special: bool = False
    in_stock: bool = True
    tags: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True

class MenuResponse(BaseModel):
    success: bool = True
    data: List[MenuItemOut]

class CanteenResponse(BaseModel):
    success: bool = True
    data: List[CanteenOut]
