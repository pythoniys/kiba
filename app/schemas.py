from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class BreweryBase(BaseModel):
    name: str
    location: Optional[str] = None
    establishment_date: Optional[date] = None

class Brewery(BreweryBase):
    id: int

    class Config:
        orm_mode = True

class BeerTypeBase(BaseModel):
    name: str
    type: Optional[str] = None
    alcohol_content: Optional[float] = None
    description: Optional[str] = None

class BeerType(BeerTypeBase):
    id: int

    class Config:
        orm_mode = True

class IngredientBase(BaseModel):
    name: str
    type: str

class Ingredient(IngredientBase):
    id: int

    class Config:
        orm_mode = True
