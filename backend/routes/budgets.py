from fastapi import APIRouter
from collections import defaultdict
from datetime import datetime
from supabase_client import supabase

router = APIRouter()

def read_transactions():
    response = supabase.table("transactions").select("*").execute()
    return response.data

@router.post("/set-budget")
def set_budget(data: dict):
    amount = data.get("amount")

    supabase.table("budgets").insert({
        "amount": amount
    }).execute()

    return {"message": "Budget saved"}

@router.get("/get-budget")
def get_budget():
    response = (
        supabase
        .table("budgets")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if len(response.data) == 0:
        return {"budget": 0}

    return {"budget": response.data[0]["amount"]}

@router.get("/budget-status")
def budget_status():
    transactions = read_transactions()

    budget_response = (
        supabase
        .table("budgets")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if len(budget_response.data) == 0:
        return {"message": "No budget set"}

    budget = budget_response.data[0]["amount"]

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

    budget_response = (
        supabase
        .table("budgets")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if len(budget_response.data) == 0:
        return {
            "budget": 0,
            "spent": 0
        }

    budget = budget_response.data[0]["amount"]

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

    supabase.table("incomes").insert({
        "amount": amount
    }).execute()

    return {"message": "Income saved"}

@router.get("/savings-status")
def savings_status():
    transactions = read_transactions()

    income_response = (
        supabase
        .table("incomes")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if len(income_response.data) == 0:
        return {"message": "No income set"}

    income = income_response.data[0]["amount"]

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

@router.post("/set-category-budget")
def set_category_budget(data: dict):
    category = data.get("category")
    amount = data.get("amount")

    if not category or amount is None:
        return {"error": "Invalid data"}

    supabase.table("category_budgets").insert({
        "category": category,
        "amount": amount
    }).execute()

    return {"message": "Category budget saved"}

@router.get("/category-budget-status")
def category_budget_status():
    transactions = read_transactions()

    budget_response = (
        supabase
        .table("category_budgets")
        .select("*")
        .execute()
    )

    budgets = budget_response.data

    current_month = datetime.now().strftime("%Y-%m")

    spent = defaultdict(float)

    for t in transactions:
        if t.get("date", "").startswith(current_month):
            spent[t["category"]] += t["amount"]

    result = []

    for item in budgets:
        cat = item["category"]
        budget = item["amount"]

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