from fastapi import APIRouter
import csv
import os
from datetime import datetime
from supabase_client import supabase

router = APIRouter()

# DATA_DIR = "data"
# FILE_PATH = os.path.join(DATA_DIR, "transactions.csv")

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DATA_DIR = os.path.join(BASE_DIR, "data")

# FILE_PATH = os.path.join(DATA_DIR, "transactions.csv")


# def read_transactions():
#     transactions = []

#     if not os.path.exists(FILE_PATH):
#         return transactions

#     with open(FILE_PATH, mode="r") as file:
#         reader = csv.DictReader(file)

#         for row in reader:
#             transactions.append({
#                 "amount": float(row["amount"]),
#                 "category": row["category"],
#                 "description": row["description"],
#                 "date": row.get("date", "")
#             })

#     return transactions


@router.post("/add-transaction")
def add_transaction(transaction: dict):

    response = supabase.table("transactions").insert({
        "amount": transaction["amount"],
        "category": transaction["category"],
        "description": transaction["description"],
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return {
        "message": "Transaction added successfully",
        "data": response.data
    }

@router.get("/transactions")
def get_transactions():

    response = (
        supabase
        .table("transactions")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

@router.delete("/delete-transaction/{id}")
def delete_transaction(id: int):

    supabase.table("transactions").delete().eq("id", id).execute()

    return {"message": "Deleted successfully"}