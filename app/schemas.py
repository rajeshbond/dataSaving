
from datetime import datetime , date
from operator import le
from pydantic import BaseModel, EmailStr , conint
from typing import Optional
from app.models import *
from pydantic.types import conlist




class UserCreate(BaseModel):
    email: EmailStr           # Check for proper email syntex 
    password : str
    name:  str
    phone: str
    date: date
    

    class Config:
        # orm_mode = True  # original 
        from_attributes = True
 
class UserOut(BaseModel):  # Select BaseMolel is we select UserCreate then password field also get inhertited by default 
    id: int
    email: EmailStr
    name: str
    phone: str
    date: date
    created_at: datetime

    
    class Config:
        # orm_mode = True  
        from_attributes = True
    
class ForgetPassword(BaseModel):
    email: EmailStr
    
    class Config:
        # orm_mode = True
        from_attributes = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str
   
    class Config:
        orm_mode = True  
class UserChangePassword(BaseModel):
    password: str
    password_new: str
    
class ForgotPasswordChange(BaseModel):
    reset_code1: str
    password: str
    
class UserForgetlink(BaseModel):
    email: str
    class Config:
        # orm_mode = True 
        from_attributes = True
class UserForgetPasswordOut(BaseModel):
    id: int
    class Config:
        # orm_mode = True 
        from_attributes = True
 
 
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
           
class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut  
    class Config:
        # orm_mode = True
        from_attributes = True

class PostOut(BaseModel):
    Post : Post
    votes : int
    class Config:
        # orm_mode = True
        from_attributes = True

    

#  auth.py Token schemas
 
class Token(BaseModel):
    access_token: str
    token_type: str
    

class TokenData(BaseModel):
    id: Optional[str] = None
    
# Schemes for voting 

# class Vote(BaseModel):
#     post_id : int
#     dir: conint(le=1)
class WatchListIn(BaseModel):
    symbol: str
class WatchListOut(BaseModel):
    symbol:str
    name_of_the_company:str
class ForgotPassword(BaseModel):
    email: EmailStr
class WatchiLstInCompany(BaseModel):
    name_of_the_company:str
  
    


   
    