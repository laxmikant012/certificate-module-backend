from typing import Optional
from datetime import date
from pydantic import BaseModel, validator


class UploadBase(BaseModel):
    
    completion_date : Optional[date]
    issued_by : Optional[str]
    designation : Optional[str]
    select_template: Optional[int]

    @validator('select_template')
    def validate_select_template_id(cls, id):
        """if selected template id does not exist it assigns to 1."""
        if id not in range(1,5):
            id= 1 
        return id
    
    class Config:
         orm_mode = True


class User(BaseModel):
    name : str
    email : str
    password : str


class Login(BaseModel):
    username : str
    password : str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None