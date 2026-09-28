from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Transactions
from schemas import TransactionCreate, TransactionUpdate, TransactionOut
from routers.auth import get_current_user

router = APIRouter(prefix='/transactions', tags=['transactions'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



@router.get('/filter', response_model=list[TransactionOut])
def filter_transactions(
    db: db_dependency,
    user: user_dependency,
    type: Optional[str] = None,
    category: Optional[str] = None,
    minimum_amount: Optional[float] = None,
    maximum_amount: Optional[float] = None,
):
    query = db.query(Transactions).filter(Transactions.owner_id == user['id'])

    if type is not None:
        query = query.filter(Transactions.type == type)
    if category is not None:
        query = query.filter(Transactions.category == category)
    if minimum_amount is not None:
        query = query.filter(Transactions.amount >= minimum_amount)
    if maximum_amount is not None:
        query = query.filter(Transactions.amount <= maximum_amount)

    return query.all()


@router.get('', response_model=list[TransactionOut])
def get_transactions(db: db_dependency, user: user_dependency):
    return db.query(Transactions).filter(Transactions.owner_id == user['id']).all()


@router.get('/{transaction_id}', response_model=TransactionOut)
def get_transaction(db: db_dependency, user: user_dependency, transaction_id: int):
    transaction = db.query(Transactions).filter(
        Transactions.id == transaction_id,
        Transactions.owner_id == user['id'],
    ).first()
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Transaction not found')
    return transaction


@router.post('', response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(db: db_dependency, user: user_dependency, new_transaction: TransactionCreate):
    transaction_model = Transactions(**new_transaction.model_dump(), owner_id=user['id'])
    db.add(transaction_model)
    db.commit()
    db.refresh(transaction_model)
    return transaction_model


@router.put('/{transaction_id}', response_model=TransactionOut)
def update_transaction(
    db: db_dependency,
    user: user_dependency,
    transaction_id: int,
    update_data: TransactionUpdate,
):
    transaction = db.query(Transactions).filter(
        Transactions.id == transaction_id,
        Transactions.owner_id == user['id'],
    ).first()
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Transaction not found')

    for key, value in update_data.model_dump().items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete('/{transaction_id}')
def delete_transaction(db: db_dependency, user: user_dependency, transaction_id: int):
    transaction = db.query(Transactions).filter(
        Transactions.id == transaction_id,
        Transactions.owner_id == user['id'],
    ).first()
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Transaction not found')

    db.delete(transaction)
    db.commit()

    return {'message': 'Transaction deleted successfully'}
