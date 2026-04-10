from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class BulkDeal(BaseModel):
    min: int
    price: float

class RetailIn(BaseModel):
    name: str
    category: str
    price: float
    image: Optional[str] = Field(alias="imageUrl", default=None)
    stock: int = Field(alias="stock", default=0)
    isDuoSync: bool = Field(alias="isDuoSync", default=False)
    duoPrice: Optional[float] = Field(alias="duoPrice", default=None)
    bulkMin: Optional[int] = Field(alias="bulkMin", default=None)
    bulkPrice: Optional[float] = Field(alias="bulkPrice", default=None)

    model_config = ConfigDict(populate_by_name=True)

class RetailOut(BaseModel):
    id: int
    name: str
    category: str
    price: float
    rating: float
    reviews: int
    image: Optional[str] = Field(validation_alias="image_url", default=None)
    stock: int = Field(validation_alias="stock_level", default=0)
    isDuoSync: bool = Field(validation_alias="is_duo_sync", default=False)
    duoPrice: Optional[float] = Field(validation_alias="duo_price", default=None)
    bulkDeal: Optional[BulkDeal] = None

    @model_validator(mode='before')
    @classmethod
    def map_bulk_deal(cls, data: Any) -> Any:
        # data can be a dict (from API) or a model object (from DB via from_attributes)
        if isinstance(data, dict):
            bulk_min = data.get('bulk_min')
            bulk_price = data.get('bulk_price')
        else:
            bulk_min = getattr(data, 'bulk_min', None)
            bulk_price = getattr(data, 'bulk_price', None)
            
        if bulk_min and bulk_price:
            # We must be careful not to overwrite if bulkDeal already exists in dict
            # but usually for DB objects it won't.
            if isinstance(data, dict):
                data['bulkDeal'] = {'min': bulk_min, 'price': bulk_price}
            else:
                # If it's a model instance, we can't easily mutate it to add a field
                # but Pydantic 'before' validator on model instance passes the object.
                # One trick is to return a dict.
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns} if hasattr(data, '__table__') else {}
                if not data_dict: # fallback for plain objects
                     data_dict = data.__dict__.copy()
                data_dict['bulkDeal'] = {'min': bulk_min, 'price': bulk_price}
                return data_dict
        return data

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class RetailResponse(BaseModel):
    success: bool = True
    data: List[RetailOut]

class SellerOut(BaseModel):
    id: str
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
    id: int
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

class RetailOrderItemIn(BaseModel):
    id: int
    quantity: int

class RetailOrderIn(BaseModel):
    items: List[RetailOrderItemIn]
    total: float

class MarketReserveIn(BaseModel):
    studentId: str

class PrintJobIn(BaseModel):
    name: str
    pages: int
    type: str  # 'bw' or 'color'
    cost: float

class PrintJobOut(BaseModel):
    id: int
    status: str
    cost: float = Field(validation_alias="cost_total")
    metadata: Dict[str, Any] = Field(validation_alias="file_metadata")

    model_config = ConfigDict(from_attributes=True)

class PrintJobResponse(BaseModel):
    success: bool = True
    data: List[PrintJobOut]
