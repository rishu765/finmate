from fastapi import APIRouter
from collections import defaultdict
from datetime import datetime
import json
import csv
import os

router = APIRouter()

# DATA_DIR = "data"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_PATH = os.path.join(DATA_DIR, "transactions.csv")
BUDGET_FILE = os.path.join(DATA_DIR, "budget.txt")
CATEGORY_BUDGET_FILE = os.path.join(DATA_DIR, "category_budget.json")
INCOME_FILE = os.path.join(DATA_DIR, "income.txt")


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


@router.post("/set-budget")
def set_budget(data: dict):
    amount = data.get("amount")

    with open(BUDGET_FILE, "w") as f:
        f.write(str(amount))

    return {"message": "Budget saved"}

@router.get("/get-budget")
def get_budget():
    if not os.path.exists(BUDGET_FILE):
        return {"budget": 0}

    with open(BUDGET_FILE, "r") as f:
        value = f.read()

    return {"budget": float(value)}

@router.get("/budget-status")
def budget_status():
    transactions = read_transactions()

    if not os.path.exists(BUDGET_FILE):
        return {"message": "No budget set"}

    with open(BUDGET_FILE, "r") as f:
        budget = float(f.read())

    current_month = datetime.now().strftime("%Y-%m")

    monthly_spend = 0

    for t in transactions:
        if t.get("date", "").startswith(current_month):
            monthly_spend += t["amount"]

    percent = (monthly_spend / budget) * 100 if budget > 0 else 0

    alert = ""

    if percent >= 100:
        alert = "🚨 Budget exceeded!"
    elif percent >= 80:
        alert = "⚠️ You have used 80% of your budget"

    return {
        "budget": budget,
        "spent": monthly_spend,
        "percent": percent,
        "alert": alert
    }


@router.get("/budget-vs-actual")
def budget_vs_actual():
    transactions = read_transactions()

    if not os.path.exists(BUDGET_FILE):
        return {"budget": 0, "spent": 0}

    with open(BUDGET_FILE, "r") as f:
        budget = float(f.read())

    current_month = datetime.now().strftime("%Y-%m")

    spent = 0

    for t in transactions:
        if t.get("date", "").startswith(current_month):
            spent += t["amount"]

    return {
        "budget": budget,
        "spent": spent
    }


@router.post("/set-income")
def set_income(data: dict):
    amount = data.get("amount", 0)

    with open(INCOME_FILE, "w") as f:
        f.write(str(amount))

    return {"message": "Income saved"}


@router.get("/savings-status")
def savings_status():
    transactions = read_transactions()

    if not os.path.exists(INCOME_FILE):
        return {"message": "No income set"}

    with open(INCOME_FILE, "r") as f:
        income = float(f.read())

    current_month = datetime.now().strftime("%Y-%m")

    total_spent = 0

    for t in transactions:
        if t.get("date", "").startswith(current_month):
            total_spent += t["amount"]

    savings = income - total_spent

    percent = (savings / income) * 100 if income > 0 else 0

    status = ""

    if percent < 10:
        status = "⚠️ Very low savings"
    elif percent < 30:
        status = "🙂 Average savings"
    else:
        status = "💪 Great savings habit"

    return {
        "income": income,
        "spent": total_spent,
        "savings": savings,
        "percent": percent,
        "status": status
    }

@router.get("/category-budgets")
def get_category_budgets():
    if not os.path.exists(CATEGORY_BUDGET_FILE):
        return {}

    with open(CATEGORY_BUDGET_FILE, "r") as f:
        return json.load(f)

@router.post("/set-category-budget")
def set_category_budget(data: dict):
    category = data.get("category")
    amount = data.get("amount")

    if not category or amount is None:
        return {"error": "Invalid data"}

    budgets = {}

    if os.path.exists(CATEGORY_BUDGET_FILE):
        with open(CATEGORY_BUDGET_FILE, "r") as f:
            budgets = json.load(f)

    budgets[category] = amount

    with open(CATEGORY_BUDGET_FILE, "w") as f:
        json.dump(budgets, f)

    return {"message": "Category budget saved"}


@router.get("/category-budget-status")
def category_budget_status():
    transactions = read_transactions()

    if not os.path.exists(CATEGORY_BUDGET_FILE):
        return []

    with open(CATEGORY_BUDGET_FILE, "r") as f:
        budgets = json.load(f)

    current_month = datetime.now().strftime("%Y-%m")

    spent = defaultdict(float)

    for t in transactions:
        if t.get("date", "").startswith(current_month):
            spent[t["category"]] += t["amount"]

    result = []

    for cat, budget in budgets.items():
        used = spent.get(cat, 0)

        percent = (used / budget) * 100 if budget > 0 else 0

        alert = ""

        if percent >= 100:
            alert = "🚨 Over budget"
        elif percent >= 80:
            alert = "⚠️ Near limit"

        result.append({
            "category": cat,
            "budget": budget,
            "spent": used,
            "percent": percent,
            "alert": alert
        })

    return result