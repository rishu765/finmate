from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import csv
from fastapi import UploadFile, File

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for now)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()
    
    reader = csv.DictReader(decoded)

    for row in reader:
        transactions.append({
            "amount": float(row["amount"]),
            "category": row["category"],
            "description": row["description"]
        })

    return {"message": "CSV uploaded successfully"}

@app.delete("/delete-transaction/{index}")
def delete_transaction(index: int):
    if 0 <= index < len(transactions):
        transactions.pop(index)
        return {"message": "Deleted successfully"}
    return {"error": "Invalid index"}