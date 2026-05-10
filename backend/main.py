from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
import json


app = FastAPI()

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

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

FILE_PATH = os.path.join(DATA_DIR, "transactions.csv")
BUDGET_FILE = os.path.join(DATA_DIR, "budget.txt")
CATEGORY_BUDGET_FILE = os.path.join(DATA_DIR, "category_budget.json")
INCOME_FILE = os.path.join(DATA_DIR, "income.txt")

# Data model
class Transaction(BaseModel):
    amount: float
    category: str
    description: str


# 🔹 READ FROM CSV
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

@app.get("/smart-summary")
def smart_summary():
    transactions = read_transactions()

    if len(transactions) == 0:
        return {"summary": "No data available"}

    # 🔹 total spend
    total_spent = sum(t["amount"] for t in transactions)

    # 🔹 category breakdown
    category_totals = {}
    for t in transactions:
        category_totals[t["category"]] = category_totals.get(t["category"], 0) + t["amount"]

    top_category = max(category_totals, key=category_totals.get)

    # 🔹 budget
    budget = 0
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            budget = float(f.read())

    budget_percent = (total_spent / budget * 100) if budget > 0 else 0

    # 🔹 savings
    income = 0
    if os.path.exists(INCOME_FILE):
        with open(INCOME_FILE, "r") as f:
            income = float(f.read())

    savings_percent = ((income - total_spent) / income * 100) if income > 0 else 0

    # 🔥 FINAL SUMMARY LOGIC
    summary = f"You spent ₹{int(total_spent)} this month. "

    summary += f"{top_category} is your top category. "

    if budget > 0:
        summary += f"You used {int(budget_percent)}% of your budget. "

    if income > 0:
        summary += f"Your savings rate is {int(savings_percent)}%. "

    # smart advice
    if budget_percent > 80:
        summary += "⚠️ You are close to exceeding your budget. "
    if savings_percent < 20:
        summary += "⚠️ Your savings are low. Try reducing discretionary spending."

    return {"summary": summary}

@app.post("/set-income")
def set_income(data: dict):
    amount = data.get("amount", 0)

    with open(INCOME_FILE, "w") as f:
        f.write(str(amount))

    return {"message": "Income saved"}

@app.get("/savings-status")
def savings_status():
    transactions = read_transactions()

    # get income
    if not os.path.exists(INCOME_FILE):
        return {"message": "No income set"}

    with open(INCOME_FILE, "r") as f:
        income = float(f.read())

    # current month
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


@app.post("/set-category-budget")
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


@app.get("/category-budgets")
def get_category_budgets():
    if not os.path.exists(CATEGORY_BUDGET_FILE):
        return {}

    with open(CATEGORY_BUDGET_FILE, "r") as f:
        return json.load(f)
    
    
@app.get("/category-budget-status")
def category_budget_status():
    transactions = read_transactions()

    if not os.path.exists(CATEGORY_BUDGET_FILE):
        return {}

    with open(CATEGORY_BUDGET_FILE, "r") as f:
        budgets = json.load(f)

    current_month = datetime.now().strftime("%Y-%m")

    spent = defaultdict(float)

    # calculate spend per category
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


# 🔹 ROOT
@app.get("/")
def read_root():
    return {"message": "FinMate backend running"}

@app.post("/set-budget")
def set_budget(data: dict):
    amount = data.get("amount")

    with open(BUDGET_FILE, "w") as f:
        f.write(str(amount))

    return {"message": "Budget saved"}

@app.get("/get-budget")
def get_budget():
    if not os.path.exists(BUDGET_FILE):
        return {"budget": 0}

    with open(BUDGET_FILE, "r") as f:
        value = f.read()

    return {"budget": float(value)}

@app.get("/budget-status")
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

@app.get("/budget-vs-actual")
def budget_vs_actual():
    transactions = read_transactions()

    # get budget
    if not os.path.exists(BUDGET_FILE):
        return {"budget": 0, "spent": 0}

    with open(BUDGET_FILE, "r") as f:
        budget = float(f.read())

    # calculate current month spend
    current_month = datetime.now().strftime("%Y-%m")
    spent = 0

    for t in transactions:
        if t.get("date", "").startswith(current_month):
            spent += t["amount"]

    return {
        "budget": budget,
        "spent": spent
    }

# 🔹 ADD TRANSACTION
@app.post("/add-transaction")
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

# 🔹 GET ALL TRANSACTIONS
@app.get("/transactions")
def get_transactions():
    return read_transactions()


# 🔹 DELETE TRANSACTION
@app.delete("/delete-transaction/{index}")
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


# 🔹 UPLOAD CSV (FIXED VERSION)
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()

    reader = csv.DictReader(decoded)

    file_exists = os.path.exists(FILE_PATH)
    
    with open(FILE_PATH, mode="a", newline="") as file_obj:
        fieldnames = ["amount", "category", "description", "date"]
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for row in reader:
            writer.writerow({
                "amount": float(row["amount"]),
                "category": row["category"],
                "description": row["description"],
                "date": datetime.now().strftime("%Y-%m-%d")
            })

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
    