from datetime import date
from pathlib import Path
import sqlite3

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DB_PATH = Path(__file__).parent / "budget.db"

CATEGORIES = [
    "Food", "Rent", "Transport", "Utilities", "Shopping",
    "Health", "Education", "Entertainment", "Savings", "Salary", "Other",
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                limit_amount REAL NOT NULL
            )"""
        )


@app.route("/")
def index():
    month = request.args.get("month") or date.today().strftime("%Y-%m")

    with get_db() as conn:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE substr(date, 1, 7) = ? "
            "ORDER BY date DESC, id DESC",
            (month,),
        ).fetchall()
        budgets = {
            r["category"]: r["limit_amount"]
            for r in conn.execute("SELECT * FROM budgets").fetchall()
        }

    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "expense")

    spent_by_category = {}
    for t in transactions:
        if t["type"] == "expense":
            spent_by_category[t["category"]] = (
                spent_by_category.get(t["category"], 0) + t["amount"]
            )

    budget_rows = []
    for cat, limit_amount in budgets.items():
        spent = spent_by_category.get(cat, 0)
        percent = (spent / limit_amount * 100) if limit_amount else 0
        budget_rows.append(
            {"category": cat, "limit": limit_amount, "spent": spent, "percent": percent}
        )

    return render_template(
        "index.html",
        month=month,
        transactions=transactions,
        income=income,
        expense=expense,
        balance=income - expense,
        categories=CATEGORIES,
        spent_by_category=spent_by_category,
        budget_rows=budget_rows,
        today=date.today().isoformat(),
    )


@app.route("/add", methods=["POST"])
def add_transaction():
    title = request.form.get("title", "").strip()
    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        amount = 0
    t_type = request.form.get("type", "expense")
    category = request.form.get("category", "Other")
    t_date = request.form.get("date") or date.today().isoformat()

    if title and amount > 0 and t_type in ("income", "expense"):
        with get_db() as conn:
            conn.execute(
                "INSERT INTO transactions (title, amount, type, category, date) "
                "VALUES (?, ?, ?, ?, ?)",
                (title, amount, t_type, category, t_date),
            )
    return redirect(url_for("index", month=t_date[:7]))


@app.route("/delete/<int:tx_id>", methods=["POST"])
def delete_transaction(tx_id):
    month = request.form.get("month", "")
    with get_db() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    return redirect(url_for("index", month=month))


@app.route("/budget", methods=["POST"])
def set_budget():
    category = request.form.get("category", "")
    month = request.form.get("month", "")
    try:
        limit_amount = float(request.form.get("limit_amount", 0))
    except ValueError:
        limit_amount = 0

    if category in CATEGORIES and limit_amount > 0:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO budgets (category, limit_amount) VALUES (?, ?) "
                "ON CONFLICT(category) DO UPDATE SET limit_amount = excluded.limit_amount",
                (category, limit_amount),
            )
    return redirect(url_for("index", month=month))


@app.route("/budget/delete/<category>", methods=["POST"])
def delete_budget(category):
    month = request.form.get("month", "")
    with get_db() as conn:
        conn.execute("DELETE FROM budgets WHERE category = ?", (category,))
    return redirect(url_for("index", month=month))


@app.template_filter("money")
def money(value):
    return f"₹{value:,.2f}"


# Create tables on startup (needed when run by gunicorn on Render too)
init_db()

if __name__ == "__main__":
    app.run(debug=True)
