from fastapi import FastAPI, Form, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import secrets
import joblib
import pandas as pd
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import json
import bcrypt
import warnings
warnings.filterwarnings('ignore')
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from masterdata import season_dict, region_dict
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None
class User(BaseModel):
    username: str
class UserInDB(User):
    hashed_password: str
class QScoreRequest(BaseModel):
    Vendor: str
    Material: str
class QScoreResponse(BaseModel):
    q_score: str
    sampling: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # อนุญาติทุก origins หรือระบุเฉพาะที่อนุญาต
    allow_credentials=True,
    allow_methods=["*"],  # หรือระบุเฉพาะ methods ที่อนุญาต ('GET', 'POST', ...)
    allow_headers=["*"],  # หรือระบุเฉพาะ headers ที่อนุญาต
)
# JWT Secret Key
SECRET_KEY = secrets.token_urlsafe(16)
ALGORITHM = "HS256"

model_path = './Linear_Cassava_Model.pkl'
model = joblib.load(model_path)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())  # This should use a proper hashing function in a real app
# Users database simulation
users_db = {}
if 'confidential' in config.sections():
    section = 'confidential'
    username = config[section]['username']
    hashed_password = config[section]['hashed_password']
    users_db[username] = {
        "username": username,
        "hashed_password": get_password_hash(hashed_password)
    }

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Token endpoint
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post('/upload')
async def upload(
    date_receive: str = Form(...),
    plant: str = Form(...),
    vendor: str = Form(...),
    fines: float = Form(...),
    bulk: float = Form(...)
):
    try:
        # ดึงเดือนจากวันที่รับข้อมูล
        month = datetime.strptime(date_receive, '%d.%m.%Y').month
        season = season_dict.get(month, 'Unknown')
        region = region_dict.get(vendor, 'Unknown')
        logging.info(f"data: month={month}, month={season}, month={region}")
        input_data = pd.DataFrame({
            'month': [month],
            'season': [season],
            'plant': [plant],
            'vendor': [vendor],
            'region': [region],
            'fines': [fines],
            'bulk': [bulk]
        })
        # input_data['vendor'] = input_data['vendor'].astype(int)
        input_data['fines'] = input_data['fines'].astype(float)
        input_data['bulk'] = input_data['bulk'].astype(float)
        logging.info(f"data: {input_data}")
        sand_predict_value = model.predict(input_data)
        sand_value = float(sand_predict_value[0])
        total_sand_value = (sand_value * input_data['fines'].iloc[0]) / 100
        sand_predict_value_rounded = round(sand_predict_value[0], 2)
        total_sand_value_rounded = round(total_sand_value, 2)
        output_data = {
            'sand_predict_value': sand_predict_value_rounded,
            'total_sand_value': total_sand_value_rounded
        }
        logging.info(f"data: sand_predict={sand_predict_value_rounded}, total_sand={total_sand_value_rounded}, output_data={output_data}")
        return output_data
    except Exception as e:
        logging.error(f"Error in upload endpoint: {e}")
        return {'error': 'An error occurred processing your request.'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)