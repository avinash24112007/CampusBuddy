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
    id: str
    canteen_id: str
    name: str
    description: Optional[str] = None
    category: str
    price: float
    prepTime: Optional[str] = Field(alias="prepTime", validation_alias="prep_time", default=None)
    image: Optional[str] = Field(alias="image", validation_alias="image_url", default=None)
    totalOrders: Optional[int] = Field(alias="totalOrders", validation_alias="total_orders", default=0)
    calories: Optional[int] = None
    isVeg: bool = Field(alias="isVeg", validation_alias="is_veg", default=True)
    is_special: bool = False
    inStock: bool = Field(alias="inStock", validation_alias="in_stock", default=True)
    availableFrom: Optional[str] = Field(alias="availableFrom", validation_alias="available_from", default=None)
    availableTo: Optional[str] = Field(alias="availableTo", validation_alias="available_to", default=None)
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

class MenuItemOut(BaseModel):
    id: str
    canteen_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    category: str
    price: float
    prepTime: Optional[str] = Field(alias="prepTime", validation_alias="prep_time", default=None)
    image: Optional[str] = Field(alias="image", validation_alias="image_url", default=None)
    rating: Optional[float] = 0.0
    totalOrders: Optional[int] = Field(alias="totalOrders", validation_alias="total_orders", default=0)
    calories: Optional[int] = None
    isVeg: bool = Field(alias="isVeg", validation_alias="is_veg", default=True)
    is_special: bool = False
    inStock: bool = Field(alias="inStock", validation_alias="in_stock", default=True)
    availableFrom: Optional[str] = Field(alias="availableFrom", validation_alias="available_from", default=None)
    availableTo: Optional[str] = Field(alias="availableTo", validation_alias="available_to", default=None)
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MenuResponse(BaseModel):
    success: bool = True
    data: List[MenuItemOut]

class CanteenResponse(BaseModel):
    success: bool = True
    data: List[CanteenOut]
