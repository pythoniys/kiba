from sqlalchemy.orm import Session
from . import models, schemas

def get_breweries(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Brewery).offset(skip).limit(limit).all()

def get_beer_types(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.BeerType).offset(skip).limit(limit).all()

def get_ingredients(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Ingredient).offset(skip).limit(limit).all()
