import imp
from fastapi import APIRouter, Depends, HTTPException, status
from hashing import Hash
import schemas, models
from database.database import get_db
from sqlalchemy.orm import Session
from .token import create_access_token
from fastapi.security import OAuth2PasswordRequestForm 

router = APIRouter()

@router.post('/login')
def login(request : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db) ):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="wrong credentails")
    
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Incorrect Password')

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}