from fastapi import FastAPI
import models
from database import engine
from routers import auth, transactions

app = FastAPI(title='Personal Expense Tracker API')

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(transactions.router)


@app.get('/')
def health_check():
    return {'status': 'ok'}
