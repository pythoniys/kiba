from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models, schemas

def get_breweries(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Brewery).offset(skip).limit(limit).all()

def get_beer_types(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.BeerType).offset(skip).limit(limit).all()

def get_ingredients(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Ingredient).offset(skip).limit(limit).all()

def get_batch(db: Session, batch_id: int):
    return db.query(models.Batch).filter(models.Batch.id == batch_id).first()

def get_remaining_volume(db: Session, batch_id: int) -> float:
    result = db.execute(text("SELECT get_remaining_volume(:batch_id)"), {"batch_id": batch_id}).fetchone()
    return result[0] if result else None

def get_batches_with_remaining_volume(db: Session, skip: int = 0, limit: int = 10):
    return db.execute(
        text("SELECT * FROM batch_with_remaining_volume LIMIT :limit OFFSET :skip"),
        {"limit": limit, "skip": skip}
    ).fetchall()


