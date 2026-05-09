import { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Tooltip,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
} from "recharts";
import { API_BASE_URL } from "./config";

function App() {
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);

  const [transactions, setTransactions] = useState([]);
  const [insights, setInsights] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [aiInsight, setAiInsight] = useState("");
  const [loadingAI, setLoadingAI] = useState(false);
  const [monthlyData, setMonthlyData] = useState([]);
  const [budget, setBudget] = useState("");
  const [budgetStatus, setBudgetStatus] = useState(null);
  const [budgetComparison, setBudgetComparison] = useState(null);
  const [categoryBudget, setCategoryBudget] = useState("");
  const [budgetCategory, setBudgetCategory] = useState("");
  const [categoryStatus, setCategoryStatus] = useState([]);
  const [income, setIncome] = useState("");
  const [savingsData, setSavingsData] = useState(null);
  const [smartSummary, setSmartSummary] = useState("");

  const categories = ["All", ...new Set(transactions.map((t) => t.category))];

  const filteredTransactions =
    selectedCategory === "All"
      ? transactions
      : transactions.filter((t) => t.category === selectedCategory);

  useEffect(() => {
    fetchTransactions();
    fetchInsights();
    fetchMonthlyTrends();
    fetchBudgetStatus();
    fetchCategoryStatus();
    fetchSavings();
    fetchBudgetComparison();
    fetchSmartSummary();
  }, []);

  const fetchSmartSummary = async () => {
    const res = await fetch(`${API_BASE_URL}/smart-summary`);
    const data = await res.json();

    setSmartSummary(data.summary);
  };

  const handleSetIncome = async () => {
    await fetch(`${API_BASE_URL}/set-income`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        amount: parseFloat(income),
      }),
    });

    setIncome("");
    fetchSavings();
  };

  const fetchSavings = async () => {
    const res = await fetch(`${API_BASE_URL}/savings-status`);
    const data = await res.json();
    setSavingsData(data);
  };

  const handleSetCategoryBudget = async () => {
    if (!budgetCategory || !categoryBudget) {
      alert("Enter category and amount");
      return;
    }

    await fetch(`${API_BASE_URL}/set-category-budget`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        category: budgetCategory,
        amount: parseFloat(categoryBudget),
      }),
    });

    setBudgetCategory("");
    setCategoryBudget("");

    fetchCategoryStatus();
  };

  const fetchCategoryStatus = async () => {
    const res = await fetch(`${API_BASE_URL}/category-budget-status`);
    const data = await res.json();
    setCategoryStatus(data);
  };

  const fetchAIInsights = async () => {
    setLoadingAI(true);

    try {
      const res = await fetch(`${API_BASE_URL}/ai-insights`);
      const data = await res.json();

      setAiInsight(data.insight || "Error generating insight");
    } catch (err) {
      setAiInsight("Error calling AI");
    }

    setLoadingAI(false);
  };

  // 🔹 FETCH TRANSACTIONS
  const fetchTransactions = async () => {
    const res = await fetch(`${API_BASE_URL}/transactions`);
    const data = await res.json();
    setTransactions(data);
  };

  // 🔹 FETCH INSIGHTS
  const fetchInsights = async () => {
    const res = await fetch(`${API_BASE_URL}/insights`);
    const data = await res.json();
    setInsights(data);
  };

  const handleSetBudget = async () => {
    await fetch(`${API_BASE_URL}/set-budget`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        amount: parseFloat(budget),
      }),
    });

    setBudget("");
    fetchBudgetStatus();
  };

  const fetchBudgetStatus = async () => {
    const res = await fetch(`${API_BASE_URL}/budget-status`);
    const data = await res.json();
    setBudgetStatus(data);
  };

  // 🔹 ADD TRANSACTION
  const handleSubmit = async () => {
    await fetch(`${API_BASE_URL}/add-transaction`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        amount: parseFloat(amount),
        category,
        description,
      }),
    });

    setAmount("");
    setCategory("");
    setDescription("");

    // ✅ REFRESH EVERYTHING
    fetchTransactions();
    fetchInsights();
    fetchMonthlyTrends();
    fetchBudgetStatus();
    fetchCategoryStatus();
    fetchSavings();
    fetchBudgetComparison();
    fetchSmartSummary();
  };

  const fetchBudgetComparison = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/budget-vs-actual`);
      const data = await res.json();

      setBudgetComparison(data);
    } catch (err) {
      console.log("Error fetching budget comparison");
    }
  };

  // 🔹 UPLOAD CSV
  const handleFileUpload = async () => {
    if (!file) return alert("Select file");

    const formData = new FormData();
    formData.append("file", file);

    await fetch(`${API_BASE_URL}/upload-csv`, {
      method: "POST",
      body: formData,
    });

    setFile(null);
    fetchTransactions();
    fetchInsights();
  };

  // 🔹 DELETE
  const handleDelete = async (index) => {
    await fetch(`${API_BASE_URL}/delete-transaction/${index}`, {
      method: "DELETE",
    });

    fetchTransactions();
    fetchInsights();
    fetchMonthlyTrends();
  };

  const fetchMonthlyTrends = async () => {
    const res = await fetch(`${API_BASE_URL}/monthly-trends`);
    const data = await res.json();

    // convert { "2026-05": 1500 } → chart format
    const formatted = Object.entries(data)
      .map(([month, value]) => ({
        month,
        amount: value,
      }))
      .sort((a, b) => a.month.localeCompare(b.month)); // sorting added

    setMonthlyData(formatted);
  };

  const chartData =
    insights && insights.category_breakdown
      ? Object.entries(insights.category_breakdown).map(([cat, val]) => ({
          name: cat,
          value: val,
        }))
      : [];

  const card = {
    background: "#1e293b",
    padding: "20px",
    borderRadius: "12px",
    marginBottom: "20px",
  };

  const input = {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "8px",
    border: "none",
  };

  const button = {
    width: "100%",
    padding: "10px",
    background: "#6366f1",
    color: "white",
    border: "none",
    borderRadius: "8px",
  };

  const buttonDark = {
    ...button,
    background: "#111827",
  };

  const txn = {
    background: "#334155",
    padding: "10px",
    borderRadius: "8px",
    marginTop: "10px",
  };

  const deleteBtn = {
    background: "#ef4444",
    color: "white",
    border: "none",
    padding: "5px 10px",
    borderRadius: "6px",
  };

  const aiBox = {
    marginTop: "10px",
    padding: "15px",
    background: "#0f172a",
    borderRadius: "10px",
  };

  return (
    <div
      style={{
        padding: "20px",
        fontFamily: "Inter, sans-serif",
        maxWidth: "900px",
        margin: "auto",
        background: "#0f172a",
        color: "white",
        minHeight: "100vh",
      }}
    >
      <h1 style={{ textAlign: "center", marginBottom: "20px" }}>
        💸 FinMate AI ok
      </h1>

      {/* 🧠 SMART SUMMARY */}
      {smartSummary && (
        <div
          style={{
            background: "#111827",
            padding: "20px",
            borderRadius: "12px",
            marginBottom: "20px",
            border: "1px solid #374151",
          }}
        >
          <h2>🧠 Smart Summary</h2>

          <p style={{ lineHeight: "1.6", marginTop: "10px" }}>{smartSummary}</p>
        </div>
      )}

      {/* ADD */}
      <div style={card}>
        <h2>Add Transaction</h2>

        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          style={input}
        />

        <input
          type="text"
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={input}
        />

        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={input}
        />

        <button onClick={handleSubmit} style={button}>
          Add Transaction
        </button>
      </div>

      {/* INSIGHTS */}
      <div style={card}>
        <h2>Insights</h2>

        {!insights ? (
          <p>Loading...</p>
        ) : insights.message ? (
          <p>No data yet</p>
        ) : (
          <>
            <p>
              <strong>Total:</strong> ₹{insights.total_spend}
            </p>
            <p>
              <strong>Top:</strong> {insights.top_category}
            </p>

            {insights.warning && (
              <p style={{ color: "#f87171" }}>⚠️ {insights.warning}</p>
            )}

            {insights.advice && (
              <p style={{ color: "#34d399" }}>💡 {insights.advice}</p>
            )}
          </>
        )}
      </div>

      {/* CHART */}
      {chartData.length > 0 && (
        <div style={card}>
          <h2>Spending Breakdown</h2>

          <PieChart width={350} height={300}>
            <Pie data={chartData} dataKey="value" outerRadius={110}>
              {chartData.map((_, i) => (
                <Cell
                  key={i}
                  fill={["#6366f1", "#22c55e", "#f59e0b", "#ef4444"][i % 4]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      )}

      {/* MONTHLY TREND */}
      {monthlyData.length > 0 && (
        <div style={{ marginTop: "30px", textAlign: "center" }}>
          <h2>📈 Monthly Spending Trend</h2>

          <LineChart width={350} height={250} data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="amount" stroke="#8884d8" />
          </LineChart>
        </div>
      )}

      {/* CATEGORY BUDGET */}
      <div style={card}>
        <h2>📊 Category Budgets</h2>

        <input
          type="text"
          placeholder="Category (Food, Travel...)"
          value={budgetCategory}
          onChange={(e) => setBudgetCategory(e.target.value)}
          style={input}
        />

        <input
          type="number"
          placeholder="Budget Amount"
          value={categoryBudget}
          onChange={(e) => setCategoryBudget(e.target.value)}
          style={input}
        />

        <button onClick={handleSetCategoryBudget} style={button}>
          Set Budget
        </button>

        {/* LIST */}
        {categoryStatus.map((c, i) => (
          <div key={i} style={{ ...txn, marginTop: "15px" }}>
            <strong>{c.category}</strong>

            <p>Budget: ₹{c.budget}</p>
            <p>Spent: ₹{c.spent}</p>
            <p>Usage: {c.percent.toFixed(1)}%</p>

            {c.alert && <p style={{ color: "#f87171" }}>{c.alert}</p>}
          </div>
        ))}
      </div>

      {/* SAVINGS TRACKER */}
      <div style={card}>
        <h2>💰 Savings Tracker</h2>

        <input
          type="number"
          placeholder="Enter Monthly Income"
          value={income}
          onChange={(e) => setIncome(e.target.value)}
          style={input}
        />

        <button onClick={handleSetIncome} style={button}>
          Set Income
        </button>

        {savingsData && !savingsData.message && (
          <div style={{ marginTop: "15px" }}>
            <p>
              <strong>Income:</strong> ₹{savingsData.income}
            </p>
            <p>
              <strong>Spent:</strong> ₹{savingsData.spent}
            </p>
            <p>
              <strong>Savings:</strong> ₹{savingsData.savings}
            </p>
            <p>
              <strong>Savings %:</strong> {savingsData.percent.toFixed(1)}%
            </p>

            <p style={{ marginTop: "10px", fontWeight: "bold" }}>
              {savingsData.status}
            </p>
          </div>
        )}
      </div>

      {/* AI */}
      <div style={card}>
        <h2>AI Advisor</h2>

        <button onClick={fetchAIInsights} style={buttonDark}>
          Generate Advice
        </button>

        {loadingAI && <p>Thinking...</p>}

        {aiInsight && (
          <div style={aiBox}>
            {aiInsight.split("\n").map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        )}
      </div>

      {/* BUDGET VS ACTUAL */}
      {budgetComparison && (
        <div style={card}>
          <h2>📊 Budget vs Actual</h2>

          <p>
            <strong>Budget:</strong> ₹{budgetComparison.budget}
          </p>
          <p>
            <strong>Spent:</strong> ₹{budgetComparison.spent}
          </p>

          <p>
            <strong>Remaining:</strong> ₹
            {budgetComparison.budget - budgetComparison.spent}
          </p>

          <p>
            <strong>Usage:</strong>{" "}
            {((budgetComparison.spent / budgetComparison.budget) * 100).toFixed(
              1,
            )}
            %
          </p>
        </div>
      )}

      <div style={card}>
        <h2>Monthly Budget</h2>

        <input
          type="number"
          placeholder="Set budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          style={input}
        />

        <button onClick={handleSetBudget} style={button}>
          Save Budget
        </button>

        {budgetStatus && !budgetStatus.message && (
          <div style={{ marginTop: "10px" }}>
            <p>
              <strong>Budget:</strong> ₹{budgetStatus.budget}
            </p>
            <p>
              <strong>Spent:</strong> ₹{budgetStatus.spent}
            </p>
            <p>
              <strong>Usage:</strong> {budgetStatus.percent.toFixed(1)}%
            </p>

            {budgetStatus.alert && (
              <p style={{ color: "red" }}>{budgetStatus.alert}</p>
            )}
          </div>
        )}
      </div>

      {/* TRANSACTIONS */}
      <div style={card}>
        <h2>Transactions</h2>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={input}
        >
          {categories.map((cat, i) => (
            <option key={i}>{cat}</option>
          ))}
        </select>

        {filteredTransactions.map((t, index) => (
          <div key={index} style={txn}>
            <strong>₹{t.amount}</strong>
            <p>
              {t.category} • {t.description}
            </p>

            <button onClick={() => handleDelete(index)} style={deleteBtn}>
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
