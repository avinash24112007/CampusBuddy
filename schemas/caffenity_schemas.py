from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class CanteenIn(BaseModel):
    id: str
    name: str
    location: str
    description: Optional[str] = None
    image: Optional[str] = Field(alias="image", validation_alias="image_url", default=None)
    is_active: bool = True

    model_config = ConfigDict(populate_by_name=True)

class CanteenOut(BaseModel):
    id: str
    name: str
    location: str
    description: Optional[str] = None
    image: Optional[str] = Field(validation_alias="image_url", default=None)
    is_active: bool

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MenuItemIn(BaseModel):
    canteen_id: str
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
    canteen_id: Optional[str] = None
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
