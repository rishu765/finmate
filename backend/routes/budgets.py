from fastapi import APIRouter, Depends
from collections import defaultdict
from datetime import datetime
from supabase_client import supabase
from auth import get_current_user

router = APIRouter()


def read_transactions(user_id):
    response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data


# SET MONTHLY BUDGET
@router.post("/set-budget")
def set_budget(
    data: dict,
    user_id: str = Depends(get_current_user)
):
    amount = data.get("amount")

    existing = (
        supabase
        .table("budgets")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if existing.data:
        supabase.table("budgets") \
            .update({"amount": amount}) \
            .eq("user_id", user_id) \
            .execute()
    else:
        supabase.table("budgets").insert({
            "amount": amount,
            "user_id": user_id
        }).execute()

    return {"message": "Budget saved"}


# GET BUDGET
@router.get("/get-budget")
def get_budget(user_id: str = Depends(get_current_user)):

    response = (
        supabase
        .table("budgets")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if not response.data:
        return {"budget": 0}

    return {"budget": response.data[0]["amount"]}


# BUDGET STATUS
@router.get("/budget-status")
def budget_status(user_id: str = Depends(get_current_user)):

    transactions = read_transactions(user_id)

    budget_response = (
        supabase
        .table("budgets")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if not budget_response.data:
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


# BUDGET VS ACTUAL
@router.get("/budget-vs-actual")
def budget_vs_actual(user_id: str = Depends(get_current_user)):

    transactions = read_transactions(user_id)

    budget_response = (
        supabase
        .table("budgets")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if not budget_response.data:
        return {"budget": 0, "spent": 0}

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


# SET INCOME
@router.post("/set-income")
def set_income(
    data: dict,
    user_id: str = Depends(get_current_user)
):
    amount = data.get("amount", 0)

    existing = (
        supabase
        .table("incomes")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if existing.data:
        supabase.table("incomes") \
            .update({"amount": amount}) \
            .eq("user_id", user_id) \
            .execute()
    else:
        supabase.table("incomes").insert({
            "amount": amount,
            "user_id": user_id
        }).execute()

    return {"message": "Income saved"}


# SAVINGS STATUS
@router.get("/savings-status")
def savings_status(user_id: str = Depends(get_current_user)):

    transactions = read_transactions(user_id)

    income_response = (
        supabase
        .table("incomes")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if not income_response.data:
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


# SET CATEGORY BUDGET
@router.post("/set-category-budget")
def set_category_budget(
    data: dict,
    user_id: str = Depends(get_current_user)
):

    category = data.get("category")
    amount = data.get("amount")

    existing = (
        supabase
        .table("category_budgets")
        .select("*")
        .eq("user_id", user_id)
        .eq("category", category)
        .execute()
    )

    if existing.data:
        supabase.table("category_budgets") \
            .update({"amount": amount}) \
            .eq("user_id", user_id) \
            .eq("category", category) \
            .execute()
    else:
        supabase.table("category_budgets").insert({
            "category": category,
            "amount": amount,
            "user_id": user_id
        }).execute()

    return {"message": "Category budget saved"}


# CATEGORY BUDGET STATUS
@router.get("/category-budget-status")
def category_budget_status(
    user_id: str = Depends(get_current_user)
):

    transactions = read_transactions(user_id)

    budget_response = (
        supabase
        .table("category_budgets")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    current_month = datetime.now().strftime("%Y-%m")

    spent = defaultdict(float)

    for t in transactions:
        if t.get("date", "").startswith(current_month):
            spent[t["category"]] += t["amount"]

    result = []

    for row in budget_response.data:

        cat = row["category"]
        budget = row["amount"]

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