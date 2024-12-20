from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class BreweryBase(BaseModel):
    name: str
    location: Optional[str] = None
    establishment_date: Optional[date] = None

class Brewery(BaseModel):
    name: str
    location: str
    establishment_date: date

class RemainingVolume(BaseModel):
    remaining_volume: float

class BatchWithRemainingVolume(BaseModel):
    batch_id: int
    beer_type_name: str
    production_date: date
    initial_volume: float
    remaining_volume: Optional[float]

    class Config:
        orm_mode = True


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
