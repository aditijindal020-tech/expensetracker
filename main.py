"""A simple command-line personal expense tracker."""

import csv
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Windows terminals may use a legacy encoding that cannot display the rupee sign.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


DATA_FILE = Path(__file__).parent / "expenses.csv"
CHARTS_FOLDER = Path(__file__).parent / "charts"
DATE_FORMAT = "%d-%m-%Y"
FIELDS = ["date", "type", "category", "description", "amount"]
CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Education",
    "Entertainment",
    "Bills",
    "Healthcare",
    "Other",
]


def load_transactions():
    """Load valid transaction dictionaries from the CSV file."""
    transactions = []
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=FIELDS).writeheader()
        return transactions

    try:
        with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    datetime.strptime(row["date"], DATE_FORMAT)
                    amount = float(row["amount"])
                    if row["type"] not in ("Income", "Expense") or amount <= 0:
                        continue
                    transactions.append(
                        {
                            "date": row["date"],
                            "type": row["type"],
                            "category": row["category"],
                            "description": row["description"],
                            "amount": amount,
                        }
                    )
                except (KeyError, TypeError, ValueError):
                    # Skip incomplete or invalid rows without stopping the app.
                    continue
    except (OSError, csv.Error) as error:
        print(f"Could not read the CSV file: {error}")
    return transactions


def save_transaction(transaction):
    """Append one transaction to the CSV file, writing a header if needed."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0
    try:
        with DATA_FILE.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            if needs_header:
                writer.writeheader()
            writer.writerow(transaction)
    except OSError as error:
        print(f"Could not save the transaction: {error}")


def get_amount():
    """Ask repeatedly until the user enters a positive number."""
    while True:
        try:
            amount = float(input("Amount: ").strip())
            if amount <= 0:
                print("Please enter an amount greater than zero.")
            else:
                return amount
        except ValueError:
            print("Please enter a valid number, such as 250 or 99.50.")


def get_date():
    """Ask for a date in day-month-year format and validate it."""
    while True:
        date_text = input("Date (DD-MM-YYYY): ").strip()
        try:
            datetime.strptime(date_text, DATE_FORMAT)
            return date_text
        except ValueError:
            print("Invalid date. Please use DD-MM-YYYY, for example 25-11-2026.")


def get_non_empty_text(prompt):
    """Return non-empty text entered by the user."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("This field cannot be empty. Please try again.")


def add_income(transactions):
    """Collect and save an income transaction."""
    print("\nAdd Income")
    amount = get_amount()
    source = get_non_empty_text("Source (for example, Salary): ")
    description = get_non_empty_text("Description: ")
    date_text = get_date()
    transaction = {
        "date": date_text,
        "type": "Income",
        "category": source,
        "description": description,
        "amount": amount,
    }
    save_transaction(transaction)
    transactions.append(transaction)
    print("Income saved successfully.")


def add_expense(transactions):
    """Collect and save an expense transaction."""
    print("\nAdd Expense")
    amount = get_amount()
    print("Categories: " + ", ".join(CATEGORIES))
    category = get_non_empty_text("Category: ")
    description = get_non_empty_text("Description: ")
    date_text = get_date()
    transaction = {
        "date": date_text,
        "type": "Expense",
        "category": category,
        "description": description,
        "amount": amount,
    }
    save_transaction(transaction)
    transactions.append(transaction)
    print("Expense saved successfully.")


def view_transactions(transactions):
    """Print all transactions in aligned columns."""
    print("\nTransactions")
    if not transactions:
        print("No transactions recorded yet.")
        return

    headers = ["Date", "Type", "Category", "Description", "Amount (₹)"]
    rows = [
        [
            item["date"],
            item["type"],
            item["category"],
            item["description"],
            f"₹{item['amount']:.2f}",
        ]
        for item in transactions
    ]
    widths = [max(len(str(row[index])) for row in [headers] + rows) for index in range(len(headers))]
    print(" | ".join(headers[index].ljust(widths[index]) for index in range(len(headers))))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(str(row[index]).ljust(widths[index]) for index in range(len(headers))))


def calculate_balance(transactions):
    """Display total income, expenses, and the remaining balance."""
    total_income = sum(item["amount"] for item in transactions if item["type"] == "Income")
    total_expenses = sum(item["amount"] for item in transactions if item["type"] == "Expense")
    balance = total_income - total_expenses
    print("\nBalance Summary")
    print(f"Total income:     ₹{total_income:.2f}")
    print(f"Total expenses:   ₹{total_expenses:.2f}")
    print(f"Remaining balance: ₹{balance:.2f}")


def get_category_totals(transactions):
    """Return a dictionary of expense totals grouped by category."""
    totals = {}
    for item in transactions:
        if item["type"] == "Expense":
            category = item["category"]
            totals[category] = totals.get(category, 0) + item["amount"]
    return totals


def category_summary(transactions):
    """Display expense totals by category and the highest-spending category."""
    totals = get_category_totals(transactions)
    print("\nCategory-wise Expense Summary")
    if not totals:
        print("No expenses recorded yet.")
        return
    for category, total in sorted(totals.items()):
        print(f"{category}: ₹{total:.2f}")
    highest_category = max(totals, key=totals.get)
    print(f"Highest spending: {highest_category} (₹{totals[highest_category]:.2f})")


def monthly_summary(transactions):
    """Use Pandas to show income, expenses, and balance for each month."""
    print("\nMonthly Summary")
    if not transactions:
        print("No transactions recorded yet.")
        return
    data_frame = pd.DataFrame(transactions)
    data_frame["date"] = pd.to_datetime(data_frame["date"], format=DATE_FORMAT)
    data_frame["month"] = data_frame["date"].dt.to_period("M")
    summary = data_frame.pivot_table(
        index="month", columns="type", values="amount", aggfunc="sum", fill_value=0
    )
    for transaction_type in ("Income", "Expense"):
        if transaction_type not in summary.columns:
            summary[transaction_type] = 0.0
    summary["Balance"] = summary["Income"] - summary["Expense"]
    summary = summary[["Income", "Expense", "Balance"]]
    summary.index = summary.index.astype(str)
    print(summary.to_string(formatters={column: "₹{:,.2f}".format for column in summary.columns}))


def generate_charts(transactions):
    """Create a category bar chart and a monthly expense trend chart."""
    expenses = [item for item in transactions if item["type"] == "Expense"]
    if not expenses:
        print("There are no expenses to chart yet. Add an expense first.")
        return

    CHARTS_FOLDER.mkdir(parents=True, exist_ok=True)
    category_totals = get_category_totals(transactions)
    plt.figure(figsize=(8, 5))
    plt.bar(category_totals.keys(), category_totals.values(), color="cornflowerblue")
    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    category_path = CHARTS_FOLDER / "category_expenses.png"
    plt.savefig(category_path)
    plt.close()

    data_frame = pd.DataFrame(expenses)
    data_frame["date"] = pd.to_datetime(data_frame["date"], format=DATE_FORMAT)
    data_frame["month"] = data_frame["date"].dt.to_period("M").astype(str)
    monthly_totals = data_frame.groupby("month")["amount"].sum().sort_index()
    plt.figure(figsize=(8, 5))
    plt.plot(monthly_totals.index, monthly_totals.values, marker="o", color="seagreen")
    plt.title("Monthly Expense Trend")
    plt.xlabel("Month")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    monthly_path = CHARTS_FOLDER / "monthly_expenses.png"
    plt.savefig(monthly_path)
    plt.close()
    print(f"Charts saved to:\n- {category_path}\n- {monthly_path}")


def main():
    """Run the menu until the user chooses Exit."""
    transactions = load_transactions()
    while True:
        print("\n===== PERSONAL EXPENSE TRACKER =====")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Transactions")
        print("4. View Balance")
        print("5. Category-wise Summary")
        print("6. Monthly Summary")
        print("7. Generate Charts")
        print("8. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_income(transactions)
        elif choice == "2":
            add_expense(transactions)
        elif choice == "3":
            view_transactions(transactions)
        elif choice == "4":
            calculate_balance(transactions)
        elif choice == "5":
            category_summary(transactions)
        elif choice == "6":
            monthly_summary(transactions)
        elif choice == "7":
            generate_charts(transactions)
        elif choice == "8":
            print("Thank you for using Personal Expense Tracker.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")


if __name__ == "__main__":
    main()
