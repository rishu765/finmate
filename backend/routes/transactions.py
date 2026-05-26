from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase_client import supabase
from auth import get_current_user
from datetime import datetime

router = APIRouter()


class Transaction(BaseModel):
    amount: float
    category: str
    description: str


# 🔹 GET USER TRANSACTIONS
@router.get("/transactions")
def get_transactions(user_id: str = Depends(get_current_user)):

    response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("user_id", user_id)
        .order("id", desc=True)
        .execute()
    )

    return response.data


# 🔹 ADD TRANSACTION
@router.post("/add-transaction")
def add_transaction(
    transaction: Transaction,
    user_id: str = Depends(get_current_user)
):

    supabase.table("transactions").insert({
        "amount": transaction.amount,
        "category": transaction.category,
        "description": transaction.description,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "user_id": user_id
    }).execute()

    return {"message": "Transaction added successfully"}


# 🔹 DELETE TRANSACTION
@router.delete("/delete-transaction/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    user_id: str = Depends(get_current_user)
):

    # delete ONLY if transaction belongs to current user
    supabase.table("transactions") \
        .delete() \
        .eq("id", transaction_id) \
        .eq("user_id", user_id) \
        .execute()

    return {"message": "Transaction deleted"}