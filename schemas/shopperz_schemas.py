from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID

class RetailIn(BaseModel):
    name: str
    category: str
    price: float
    image: Optional[str] = Field(alias="imageUrl", default=None)
    stock: int = Field(alias="stock", default=0)
    isDuoSync: bool = Field(alias="isDuoSync", default=False)
    duoPrice: Optional[float] = Field(alias="duoPrice", default=None)

    model_config = ConfigDict(populate_by_name=True)

class RetailOut(BaseModel):
    id: UUID
    name: str
    category: str
    price: float
    rating: float
    reviews: int
    image: Optional[str] = Field(validation_alias="image_url", default=None)
    stock: int = Field(validation_alias="stock_level", default=0)
    isDuoSync: bool = Field(validation_alias="is_duo_sync", default=False)
    duoPrice: Optional[float] = Field(validation_alias="duo_price", default=None)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class RetailResponse(BaseModel):
    success: bool = True
    data: List[RetailOut]

class SellerOut(BaseModel):
    id: UUID
    name: str
    avatar: Optional[str] = Field(validation_alias="avatar_url", default=None)
    trustScore: int = Field(validation_alias="trust_score", default=100)
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MarketIn(BaseModel):
    title: str
    condition: str
    price: float
    originalPrice: Optional[float] = Field(alias="originalPrice", default=None)
    image: Optional[str] = Field(alias="imageUrl", default=None)

    model_config = ConfigDict(populate_by_name=True)

class MarketOut(BaseModel):
    id: UUID
    title: str
    condition: str
    seller: SellerOut
    price: float
    originalPrice: Optional[float] = Field(validation_alias="original_price", default=None)
    status: str
    image: Optional[str] = Field(validation_alias="image_url", default=None)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MarketResponse(BaseModel):
    success: bool = True
    data: List[MarketOut]
