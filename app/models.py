from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Brewery(Base):
    __tablename__ = "breweries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    establishment_date = Column(Date)
        

class BeerType(Base):
    __tablename__ = "beer_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    alcohol_content = Column(Float)
    description = Column(String)

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    recipe_name = Column(String)
    description = Column(String)
    beer_type_id = Column(Integer, ForeignKey("beer_types.id"))

    beer_type = relationship("BeerType")

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    beer_type_id = Column(Integer, ForeignKey("beer_types.id"))
    production_date = Column(Date)
    volume = Column(Float)

    beer_type = relationship("BeerType")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    sale_date = Column(Date)
    quantity = Column(Float)
    price = Column(Float)

    batch = relationship("Batch")
