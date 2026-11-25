# Personal Expense Tracker

## Project description

Personal Expense Tracker is a local desktop app for recording income and expenses, checking a running balance, and reviewing spending by category and month. The interface is built with Tkinter, while transactions remain in a simple CSV file.

## Features

- Dashboard cards show total income, expenses, current balance, and transaction count.
- Add income or expense with amount, source/category, description, and date.
- Validate positive amounts, required text, and real dates in `DD-MM-YYYY` format.
- View transaction history with income and expense amounts highlighted in different colors.
- Review the highest-spending category and monthly income, expense, and balance totals.
- View category and monthly income/expense charts that refresh when a transaction is added.
- Keep data between runs in `expenses.csv`.
- Save chart images in the `charts` folder.

## Technologies used

- Python 3
- Tkinter and `ttk` for the desktop interface (included with most Python installations on Windows)
- CSV and `datetime` for saving transactions and validating dates
- Pandas for monthly analysis
- Matplotlib for embedded charts and saved PNG charts
- Lists and dictionaries for transaction records and category totals

## Installation requirements

Use Python 3.10 or newer. Install the third-party packages from a terminal in this folder:

```bash
pip install -r requirements.txt
```

This installs Pandas and Matplotlib. Tkinter normally comes with the Windows Python installer; if `import tkinter` fails, rerun the Python installer and enable the Tcl/Tk option.

## How to run

In the VS Code terminal, open this project folder and run:

```bash
python main.py
```

This opens the dashboard window. The original command-line menu is still available by running `python -c "import main; main.cli_main()"`.

## Basic usage

1. Select **Income** or **Expense** in the Add transaction form.
2. Enter an amount greater than zero, a source/category, a description, and a valid date such as `25-11-2026`.
3. Select **Add transaction**. The new record is appended to `expenses.csv` and the dashboard refreshes.
4. Use the sidebar to jump to the dashboard, form, transaction list, or analytics.

An income source is saved in the CSV `category` column, such as `Salary`. Expense categories can be selected from the suggested list. The CSV starts empty except for its column headings; the app does not insert example transactions.

## Project structure

```text
PersonalExpenseTracker/
├── main.py           # CSV backend and original command-line functions
├── gui.py            # Tkinter dashboard
├── expenses.csv      # Persistent transaction data
├── requirements.txt  # Pandas and Matplotlib dependencies
├── README.md
└── charts/           # Generated category and monthly PNG charts
```

## Python concepts demonstrated

The project uses variables, input/output, conditional statements, loops, functions, lists, dictionaries, modular programming, exception handling, CSV reading/writing, and `datetime`. Pandas creates the monthly summary, and Matplotlib draws the charts.

## Possible future improvements

- Add editing and deletion for saved transactions.
- Add date filters and user-defined monthly budgets.
- Allow the user to export a monthly summary as a report.
- Add more accessible keyboard navigation and chart descriptions.
