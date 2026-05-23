from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
import json
from routes.transactions import router as transaction_router
from routes.budgets import router as budget_router
from supabase_client import supabase


app = FastAPI()
app.include_router(transaction_router)
app.include_router(budget_router)

load_dotenv()

client = OpenAI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model
class Transaction(BaseModel):
    amount: float
    category: str
    description: str

def read_transactions():
    response = supabase.table("transactions").select("*").execute()

    return response.data


@app.get("/smart-summary")
def smart_summary():
    transactions = read_transactions()

    if len(transactions) == 0:
        return {"summary": "No data available"}

    total_spent = sum(t["amount"] for t in transactions)

    # category totals
    category_totals = {}

    for t in transactions:
        category_totals[t["category"]] = (
            category_totals.get(t["category"], 0)
            + t["amount"]
        )

    top_category = max(category_totals, key=category_totals.get)

    # 🔹 GET BUDGET FROM SUPABASE
    budget_response = (
        supabase
        .table("budgets")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    budget = 0

    if len(budget_response.data) > 0:
        budget = budget_response.data[0]["amount"]

    budget_percent = (
        (total_spent / budget) * 100
        if budget > 0 else 0
    )

    # 🔹 GET INCOME FROM SUPABASE
    income_response = (
        supabase
        .table("incomes")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    income = 0

    if len(income_response.data) > 0:
        income = income_response.data[0]["amount"]

    savings_percent = (
        ((income - total_spent) / income) * 100
        if income > 0 else 0
    )

    # SUMMARY
    summary = f"You spent ₹{int(total_spent)} this month. "

    summary += f"{top_category} is your top category. "

    if budget > 0:
        summary += f"You used {int(budget_percent)}% of your budget. "

    if income > 0:
        summary += f"Your savings rate is {int(savings_percent)}%. "

    # advice
    if budget_percent > 80:
        summary += "⚠️ You are close to exceeding your budget. "

    if savings_percent < 20:
        summary += (
            "⚠️ Your savings are low. "
            "Try reducing discretionary spending."
        )

    return {
        "summary": summary
    }

# 🔹 ROOT
@app.get("/")
def read_root():
    return {"message": "FinMate backend running"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()

    import csv

    reader = csv.DictReader(decoded)

    for row in reader:
        supabase.table("transactions").insert({
            "amount": float(row["amount"]),
            "category": row["category"],
            "description": row["description"],
            "date": datetime.now().strftime("%Y-%m-%d")
        }).execute()

    return {"message": "CSV uploaded successfully"}

@app.get("/insights")
def get_insights():
    transactions = read_transactions()

    if len(transactions) == 0:
        return {"message": "No data"}

    total = 0
    category_totals = {}

    for t in transactions:
        total += t["amount"]

        if t["category"] in category_totals:
            category_totals[t["category"]] += t["amount"]
        else:
            category_totals[t["category"]] = t["amount"]

    # Top category
    top_category = max(category_totals, key=category_totals.get)

    # Simple AI logic
    warning = ""
    advice = ""

    if category_totals[top_category] > total * 0.5:
        warning = f"You are spending too much on {top_category}"
        advice = f"Try reducing {top_category} expenses by 20%"

    return {
        "total_spend": total,
        "top_category": top_category,
        "category_breakdown": category_totals,  # ✅ FIXED
        "warning": warning,
        "advice": advice
    }
    
    
@app.get("/monthly-trends")
def monthly_trends():
    transactions = read_transactions()

    monthly_data = defaultdict(float)

    for t in transactions:
        if not t.get("date"):
            continue

        month = t["date"][:7]  # YYYY-MM
        monthly_data[month] += t["amount"]

    return monthly_data

@app.get("/ai-insights")
def ai_insights():
    try:
        transactions = read_transactions()

        if len(transactions) == 0:
            return {"insight": "No transactions available"}

        summary = ""
        for t in transactions:
            summary += f"{t['category']} - ₹{t['amount']} - {t['description']}\n"

        prompt = f"""
        You are a smart financial advisor.

        Analyze the user's spending:

        {summary}

        Give:
        1. Key observation
        2. Problem area
        3. Actionable advice

        Keep it short (3-4 lines max).
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return {
            "insight": response.choices[0].message.content
        }

    except Exception as e:
        return {"error": str(e)} 