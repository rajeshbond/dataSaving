from os import access
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..import database, schemas, models,utls, oauth2



router = APIRouter(tags=['Authentication'])

@router.post('/login',response_model= schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.username.lower()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail= "Invalid credentials")
    
    if not utls.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Invalid credentials")

    if not user.is_verified_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail= f"{user.email} user not varifed ")
        
    print(f"================{user.is_verified_user}")
    
    # CREATE TOKEN 
    access_token= oauth2.create_access_token(data= {"user_id": user.id})
    return {"access_token":access_token, "token_type":"bearer"} 
        
    