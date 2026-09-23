from fastapi import FastAPI, Depends,HTTPException,Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from models import Transactions
from typing import Annotated
from database import engine,SessionLocal
from fastapi.responses import JSONResponse
from typing import Optional
from router import auth
from datetime import date
from router.auth import get_current_user
from typing import Optional,Literal
import datetime

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class Transaction(BaseModel):
    title : str
    amount : float
    type : Literal["income","expense"]
    category :str
    date : date

class UpdateTransaction(BaseModel):
    title : Optional[str] = Field(default=None)
    amount : Optional[float] = Field(default=None)
    type : Optional[Literal["income","expense"]] = Field(default=None)
    category :Optional[str] = Field(default=None)
    date : Optional[datetime.date] = Field(default=None)



@app.get("/transactions/filter")
def filter_transactions(db: db_dependency,user: user_dependency,type: Optional[str] = Query(
        None, description="Filter by type: income or expense"
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    minimum_amount: Optional[float] = Query(
        None, description="Minimum amount limit"
    ),
    maximum_amount: Optional[float] = Query(
        None, description="Maximum amount limit"
    ),
   ):
    query = db.query(Transactions).filter(
        Transactions.owner_id == user.get("id")
    )
    if type:
        query = query.filter(Transactions.type == type)

    if category:
        query = query.filter(Transactions.category == category)

    
    if minimum_amount is not None:
        query = query.filter(Transactions.amount >= minimum_amount)


    if maximum_amount is not None:
        query = query.filter(Transactions.amount <= maximum_amount)

    transactions = query.all()

    return transactions

@app.post("/transactions")
def create_transactions(user:user_dependency, db: db_dependency, new_transactions:Transaction):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transactions_model = Transactions(**new_transactions.model_dump(),owner_id=user.get("id"))
    db.add(transactions_model)
    db.commit()
    return JSONResponse(status_code=201, content={'message' : 'Transaction created successfully'})

@app.get("/transactions")
def read_transactions(user:user_dependency, db: db_dependency):
    if user is None:
         raise HTTPException(status_code=401, detail='Failed Authentication')
    
    return db.query(Transactions).filter(Transactions.owner_id == user.get('id')).all()


@app.get("/transactions/{transaction_id}")
def read_specific_transactions(user:user_dependency, db: db_dependency,transactions_id:int):
    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
     
    specific_transactions = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transactions_id).first()
    if specific_transactions is not None:
        return specific_transactions
    else:
        raise HTTPException(status_code=404, detail='To do not found')



@app.put('/transactions/{transaction_id}')
def update_todos(user: user_dependency, db : db_dependency, transaction_id : int, update_transaction : UpdateTransaction):

    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')
    
    transactions = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).first()
    if transactions is  None:
        raise HTTPException(status_code=404, detail='Transactions not found')
    
    update_data = update_transaction.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(transactions,key,value)
    
    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'Transaction updated successfully'})


@app.delete('/transactions/{transaction_id}')
def delete_todos(user: user_dependency, db : db_dependency, transaction_id : int):

    if user is None: 
        raise HTTPException(status_code=401, detail='Failed Authentication')

    todo = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).first()
    if todo is  None:
        raise HTTPException(status_code=404, detail='Transaction not found')
    
    db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).delete()
    
    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'Transaction deleted successfully'})

