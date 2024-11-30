from urllib import response
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session, relationship
from . import crud, models, schemas, database
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from fastapi.responses import FileResponse

app = FastAPI()

# static_path = Path(__file__).parent.parent / "static/frontend"
# app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

# app.mount("/", StaticFiles(directory="static/frontend", html=True), name="static")

# Путь к статическим файлам
static_path = Path(__file__).parent.parent / "static/frontend"

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Рендерим index.html на корневом маршруте
@app.get("/")
def read_root():
    return FileResponse(static_path / "index.html")

Base = declarative_base()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка шифрования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "kibochka"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30




# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# Создаем таблицы
Base.metadata.create_all(bind=database.engine)

# Функция для получения сессии базы данных
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Модель для передачи данных пользователя
class UserCreate(BaseModel):
    username: str
    password: str

# Модель для токена
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


@app.post("/register/", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# POST запрос для аутентификации пользователя
@app.post("/login/", response_model=Token)
async def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

###########################################################################

@app.get("/breweries/", response_model=list[schemas.Brewery])
def read_breweries(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    if Depends(get_current_user) :
        breweries = crud.get_breweries(db, skip=skip, limit=limit)
        return breweries

@app.get("/beer_types/", response_model=list[schemas.BeerType])
def read_beer_types(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    if Depends(get_current_user):
        beer_types = crud.get_beer_types(db, skip=skip, limit=limit)
        return beer_types

@app.get("/ingredients/", response_model=list[schemas.Ingredient])
def read_ingredients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    if Depends(get_current_user):
        ingredients = crud.get_ingredients(db, skip=skip, limit=limit)
        return ingredients

@app.get("/remaining_volume/", response_model=schemas.RemainingVolume)
def read_remaining_volume(batch_id: int, db: Session = Depends(get_db)):

    if not crud.get_batch(db, batch_id=batch_id):
        raise HTTPException(status_code=404, detail="Batch not found")
    
    remaining_volume = crud.get_remaining_volume(db, batch_id=batch_id)
    if remaining_volume is None:
        raise HTTPException(status_code=500, detail="Failed to calculate remaining volume")
    
    return {"remaining_volume": remaining_volume}

@app.get("/batches_with_volume/", response_model=list[schemas.BatchWithRemainingVolume])
def read_batches_with_volume(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    if Depends(get_current_user):
        return crud.get_batches_with_remaining_volume(db, skip=skip, limit=limit)

# POST запрос для вставки данных
@app.post("/breweries/")
async def create_brewery(request: Request,brewery: dict, db: Session = Depends(get_db)):
    print(brewery)

    new_brewery = models.Brewery(
        name=brewery['name'],
        location=brewery['location'],
        establishment_date=brewery['establishment_date']
    )
    db.add(new_brewery)
    db.commit()
    db.refresh(new_brewery)
    return "Brewery created successfully"

@app.post("/sale/")
async def create_sales(request: Request,sale: dict, db: Session = Depends(get_db)):
    print(sale)
    new_sale = models.Sale(
        batch_id=sale['batch_id'],
        sale_date=sale['sale_date'],
        quantity=sale['quantity'],
        price=sale['price']

    )
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return "Sale created successfully"


# POST запрос для удаления данных
@app.post("/breweries/delete/{brewery_id}")
async def delete_brewery(brewery_id: int, db: Session = Depends(get_db)):
    if Depends(get_current_user):
        brewery = db.query(models.Brewery).filter(models.Brewery.id == brewery_id).first()
        if not brewery:
            raise HTTPException(status_code=404, detail="Brewery not found")
        
        db.delete(brewery)
        db.commit()
        return {"message": f"Brewery with ID {brewery_id} deleted successfully"}
