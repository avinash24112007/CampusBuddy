from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import time, datetime

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
    isVeg: Optional[bool] = Field(alias="isVeg", validation_alias="is_veg", default=True)
    is_special: Optional[bool] = False
    inStock: Optional[bool] = Field(alias="inStock", validation_alias="in_stock", default=True)
    availableFrom: Optional[time] = Field(alias="availableFrom", validation_alias="available_from", default=None)
    availableTo: Optional[time] = Field(alias="availableTo", validation_alias="available_to", default=None)
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
    isVeg: Optional[bool] = Field(alias="isVeg", validation_alias="is_veg", default=True)
    is_special: Optional[bool] = False
    inStock: Optional[bool] = Field(alias="inStock", validation_alias="in_stock", default=True)
    availableFrom: Optional[time] = Field(alias="availableFrom", validation_alias="available_from", default=None)
    availableTo: Optional[time] = Field(alias="availableTo", validation_alias="available_to", default=None)
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MenuResponse(BaseModel):
    success: bool = True
    data: List[MenuItemOut]

class CanteenResponse(BaseModel):
    success: bool = True
    data: List[CanteenOut]


class OrderItemDetail(BaseModel):
    id: str = Field(validation_alias="menu_item_id")
    name: str = Field(validation_alias="name")
    quantity: int
    price: float = Field(validation_alias="price_at_time_of_order")

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: str = Field(alias="id", validation_alias="order_number")
    studentName: str = Field(alias="studentName", validation_alias="student_name")
    canteenId: str = Field(alias="canteenId", validation_alias="canteen_id")
    items: List[OrderItemDetail]
    total: float = Field(alias="total", validation_alias="total_amount")
    status: str
    timestamp: datetime = Field(alias="timestamp", validation_alias="created_at")
    scheduledTime: Optional[str] = Field(alias="scheduledTime", validation_alias="scheduled_time", default=None)
    paymentMethod: Optional[str] = Field(alias="paymentMethod", validation_alias="payment_method", default="UPI")
    paymentStatus: Optional[str] = Field(alias="paymentStatus", validation_alias="payment_status", default="Paid")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OrderResponse(BaseModel):
    success: bool = True
    data: List[OrderOut]


class OrderItemIn(BaseModel):
    id: str = Field(alias="id")
    quantity: int

    model_config = ConfigDict(populate_by_name=True)


class OrderIn(BaseModel):
    items: List[OrderItemIn]
    canteenId: str = Field(alias="canteenId")
    scheduledTime: Optional[str] = Field(alias="scheduledTime", default="As soon as possible")
    paymentMethod: str = Field(alias="paymentMethod", default="UPI")
    specialNote: Optional[str] = Field(alias="specialNote", default=None)

    model_config = ConfigDict(populate_by_name=True)
