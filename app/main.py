from urllib import response
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, relationship
from . import crud, models, schemas, database
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
Base = declarative_base()

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

# Хелпер для хеширования паролей
def get_password_hash(password):
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Создание токена доступа
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Функция для получения текущего пользователя
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


# POST запрос для регистрации пользователя
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

# POST запрос для вставки данных
@app.post("/breweries/")
async def create_brewery(name: str, location: str, establishment_date: str, db: Session = Depends(get_db)):
    if Depends(get_current_user):
        new_brewery = models.Brewery(name=name, location=location, establishment_date=establishment_date)
        db.add(new_brewery)
        db.commit()
        db.refresh(new_brewery) 
        return {"message": "Brewery created successfully", "brewery": new_brewery}

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
