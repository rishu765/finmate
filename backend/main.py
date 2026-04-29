from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Temporary storage (in-memory)
transactions = []

# Data model
class Transaction(BaseModel):
    amount: float
    category: str
    description: str

@app.get("/")
def read_root():
    return {"message": "FinMate backend running"}

# Add transaction API
@app.post("/add-transaction")
def add_transaction(transaction: Transaction):
    transactions.append(transaction)
    return {"message": "Transaction added", "data": transaction}

# Get all transactions
@app.get("/transactions")
def get_transactions():
    return transactions