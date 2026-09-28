from datetime import date
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TransactionCreate(BaseModel):
    title: str
    amount: float = Field(gt=0)
    type: Literal['income', 'expense']
    category: str
    date: date


class TransactionUpdate(BaseModel):
    title: str
    amount: float = Field(gt=0)
    type: Literal['income', 'expense']
    category: str
    date: date


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: float
    type: str
    category: str
    date: date
    owner_id: int
