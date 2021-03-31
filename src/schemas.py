
from pydantic import BaseModel
from typing import Optional

class Note(BaseModel):
    title: str
    note: str
    note_file: str

class User(BaseModel):
    name: str
    email: str
    password: str

class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str]