from pydantic import BaseModel, Field
from typing import Optional

class FoodSearchInput(BaseModel):
    keyword: Optional[str] = Field(None, description="General search keywords from the user like 'spicy', 'dosa', 'combos'.")
    category: Optional[str] = Field(None, description="Food category, like 'South Indian', 'Beverages', 'Snacks'.")
    canteen: Optional[str] = Field(None, description="The name of the canteen to search in, like 'Container'.")
    max_price: Optional[int] = Field(None, description="The maximum price in rupees the student is willing to pay.")
    min_price: Optional[int] = Field(None, description="The minimum price in rupees.")
    only_available: bool = Field(True, description="Whether to filter only currently available/in-stock items. Default generally is true.")
