import { useState, useEffect } from "react";

function App() {
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [insights, setInsights] = useState({});
  const [selectedCategory, setSelectedCategory] = useState("All");

  const categories = ["All", ...new Set(transactions.map((t) => t.category))];

  const filteredTransactions =
    selectedCategory === "All"
      ? transactions
      : transactions.filter((t) => t.category === selectedCategory);

  const fetchTransactions = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/transactions");
      const data = await response.json();
      setTransactions(data);
      calculateInsights(data);
    } catch (error) {
      console.error("Error fetching transactions:", error);
    }
  };

  const calculateInsights = (data) => {
    let total = 0;
    let categoryTotals = {};

    data.forEach((t) => {
      total += t.amount;

      if (categoryTotals[t.category]) {
        categoryTotals[t.category] += t.amount;
      } else {
        categoryTotals[t.category] = t.amount;
      }
    });

    let result = {};

    for (let category in categoryTotals) {
      result[category] = {
        total: categoryTotals[category],
        percent: ((categoryTotals[category] / total) * 100).toFixed(1),
      };
    }

    setInsights(result);
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const handleSubmit = async () => {
    try {
      await fetch("http://127.0.0.1:8000/add-transaction", {
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

      fetchTransactions();

      setAmount("");
      setCategory("");
      setDescription("");
    } catch (error) {
      console.error("Error adding transaction:", error);
    }
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      await fetch("http://127.0.0.1:8000/upload-csv", {
        method: "POST",
        body: formData,
      });

      fetchTransactions();
      setFile(null);
      alert("CSV uploaded successfully!");
    } catch (error) {
      console.error("Error uploading CSV:", error);
    }
  };

  const handleDelete = async (index) => {
    try {
      await fetch(`http://127.0.0.1:8000/delete-transaction/${index}`, {
        method: "DELETE",
      });

      fetchTransactions();
    } catch (error) {
      console.error("Error deleting:", error);
    }
  };

  return (
    <div
      style={{
        padding: "30px",
        fontFamily: "Arial",
        maxWidth: "700px",
        margin: "auto",
      }}
    >
      <h1 style={{ textAlign: "center" }}>💸 FinMate</h1>

      {/* Add Transaction */}
      <div
        style={{
          marginTop: "30px",
          padding: "20px",
          border: "1px solid #ddd",
          borderRadius: "10px",
        }}
      >
        <h2>Add Transaction</h2>

        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          style={{ width: "100%", padding: "8px", marginBottom: "10px" }}
        />

        <input
          type="text"
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={{ width: "100%", padding: "8px", marginBottom: "10px" }}
        />

        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={{ width: "100%", padding: "8px", marginBottom: "10px" }}
        />

        <button
          onClick={handleSubmit}
          style={{ width: "100%", padding: "10px" }}
        >
          Add Transaction
        </button>
      </div>

      {/* Upload CSV */}
      <div
        style={{
          marginTop: "20px",
          padding: "20px",
          border: "1px solid #ddd",
          borderRadius: "10px",
        }}
      >
        <h2>Upload CSV</h2>

        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <br />
        <br />

        <button
          onClick={handleFileUpload}
          style={{ padding: "10px", width: "100%" }}
        >
          Upload CSV
        </button>
      </div>

      {/* Transactions */}
      <div style={{ marginTop: "20px" }}>
        <h2>Transactions</h2>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={{ padding: "8px", marginBottom: "10px" }}
        >
          {categories.map((cat, index) => (
            <option key={index} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        {filteredTransactions.length === 0 ? (
          <p>No transactions found</p>
        ) : (
          filteredTransactions.map((t) => {
            const originalIndex = transactions.indexOf(t);

            return (
              <div
                key={originalIndex}
                style={{
                  padding: "10px",
                  marginBottom: "10px",
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                }}
              >
                <strong>₹{t.amount}</strong>
                <br />
                {t.category} • {t.description}
                <br />
                <br />
                <button
                  onClick={() => handleDelete(originalIndex)}
                  style={{
                    backgroundColor: "red",
                    color: "white",
                    border: "none",
                    padding: "5px 10px",
                    borderRadius: "5px",
                    cursor: "pointer",
                  }}
                >
                  Delete
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Insights */}
      <div style={{ marginTop: "20px" }}>
        <h2>Insights</h2>

        {Object.keys(insights).length === 0 ? (
          <p>No insights yet</p>
        ) : (
          Object.entries(insights).map(([category, data], index) => (
            <div
              key={index}
              style={{
                padding: "10px",
                marginBottom: "10px",
                backgroundColor: "#f5f5f5",
                borderRadius: "8px",
              }}
            >
              <strong>{category}</strong> — ₹{data.total} ({data.percent}%)
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
