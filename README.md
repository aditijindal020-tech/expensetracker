# Personal Expense Tracker

## 1. Project description

Personal Expense Tracker is a beginner-friendly command-line program for recording income and expenses, reviewing a budget, and seeing simple spending summaries. Transactions are kept in a CSV file so they are still available after the program closes.

## 2. Features

- Add income with a source, description, amount, and date.
- Add expenses with a category, description, amount, and date.
- View the transaction list and overall balance.
- See expense totals by category and the highest-spending category.
- See monthly income, expenses, and balance in a Pandas table.
- Create category and monthly expense charts in the `charts` folder.
- Validate entered amounts and dates.

## 3. Technologies used

- Python 3
- CSV file handling
- `datetime` for date validation and month grouping
- Pandas for the monthly summary and chart data
- Matplotlib for charts
- Lists and dictionaries for transaction data and category totals

## 4. Project structure

```text
PersonalExpenseTracker/
├── main.py
├── expenses.csv
├── README.md
└── charts/                 # Created when charts are generated
```

## 5. Install dependencies

Install Python 3 if it is not already available, then install the two Python packages used by the reports and charts:

```bash
pip install pandas matplotlib
```

## 6. Run the project

Open a terminal in this folder and run:

```bash
python main.py
```

The program loads `expenses.csv` on startup. New transactions are appended to that file immediately. An empty CSV is normal; the project starts without sample transactions.

## 7. Example usage

Choose `1` to add income. For example, enter an amount of `25000`, a source of `Salary`, a description such as `Monthly salary`, and a date such as `25-11-2026`.

Choose `2` to add an expense, such as `500` in the `Food` category with the description `Lunch`. Dates must use `DD-MM-YYYY`. Use the menu to view transactions, balance, summaries, or generate charts. Chart files are saved as `charts/category_expenses.png` and `charts/monthly_expenses.png`.

## 8. Python concepts demonstrated

The program demonstrates variables, input and output, `if`/`elif`/`else`, loops, functions, lists, dictionaries, exception handling, CSV reading and writing, and date handling with `datetime`. Pandas creates a DataFrame and groups data by month. Matplotlib draws and saves charts.

## 9. Future improvements

- Allow transactions to be edited or deleted.
- Add date-range filtering and monthly budgets.
- Let the user choose from the suggested categories with a numbered list.
- Export a report for a selected month.
