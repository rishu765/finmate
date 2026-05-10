from fastapi import APIRouter
import csv
import os
from datetime import datetime

router = APIRouter()

# DATA_DIR = "data"
# FILE_PATH = os.path.join(DATA_DIR, "transactions.csv")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_PATH = os.path.join(DATA_DIR, "transactions.csv")


def read_transactions():
    transactions = []

    if not os.path.exists(FILE_PATH):
        return transactions

    with open(FILE_PATH, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            transactions.append({
                "amount": float(row["amount"]),
                "category": row["category"],
                "description": row["description"],
                "date": row.get("date", "")
            })

    return transactions


@router.post("/add-transaction")
def add_transaction(transaction: dict):
    file_exists = os.path.exists(FILE_PATH)

    with open(FILE_PATH, mode="a", newline="") as file:
        fieldnames = ["amount", "category", "description", "date"]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "amount": transaction["amount"],
            "category": transaction["category"],
            "description": transaction["description"],
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    return {"message": "Transaction added successfully"}


@router.get("/transactions")
def get_transactions():
    return read_transactions()


@router.delete("/delete-transaction/{index}")
def delete_transaction(index: int):
    transactions = read_transactions()

    if index < 0 or index >= len(transactions):
        return {"error": "Invalid index"}

    transactions.pop(index)

    with open(FILE_PATH, mode="w", newline="") as file:
        fieldnames = ["amount", "category", "description", "date"]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for t in transactions:
            writer.writerow(t)

    return {"message": "Deleted successfully"}