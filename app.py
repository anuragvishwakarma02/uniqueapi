from fastapi import FastAPI,HTTPException
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from pydantic import BaseModel # Most widely used data validation library for python
from typing import List # Supports for type hints
import consts
from users import login

# define a lifespan method for fastapi
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the database connection
    await startup_db_client(app)
    yield
    # Close the database connection
    await shutdown_db_client(app)

# method for start the MongoDb Connection
async def startup_db_client(app):
    app.mongodb_client = AsyncIOMotorClient(consts.MONGODB_CONNETION_STRING)
    app.mongodb = app.mongodb_client.get_database("uniqueacademy")
    print("MongoDB connected.")

# method to close the database connection
async def shutdown_db_client(app):
    app.mongodb_client.close()
    print("Database disconnected.")

# creating a server with python FastAPI
app = FastAPI(lifespan=lifespan,
               title="ChimichangApp",
    description="description",
    summary="Deadpool's favorite app. Nuff said.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    )

@app.get("/health")
async def health():
    return {"message":"I am up"}


# @app.get("/")
# async def root():
#     # result = await app.mongodb["users"].insert_one({"email":"asd",'name':'Anurag'})
#     result =  app.mongodb["users"].find({"email":"asd"})
#     print(list(result))
#     return {"message":"sadsad"}


@app.get("/get_token")
async def get_token():
    return login.get_token()
    

@app.get("/verify_token")
async def verify_token():
    return login.verify_token()



class User(BaseModel):
    mobile: str

class UserSignup(BaseModel):
    mobile: str
    otp: str 

@app.get('/get_otp/')
async def user_sign_in(mobile):
    return {'otp':mobile[-4:]}


@app.post('sign-in',status_code=200)
async def user_sign_in(user:UserSignup):
    if user.otp is user.mobile[-4:]:
        user_present = await app.mongodb["users"].find_one({"mobile":user})
        if user_present is None:        
            #Insert that user
            await app.mongodb["users"].insert_one({"mobile":user})
        current_user = await app.mongodb["users"].find_one({"mobile":user})
    else:
        raise HTTPException(status_code=401, detail="Invalid OTP")
    return login.get_token(current_user)
    
        

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)