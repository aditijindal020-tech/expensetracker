import csv
from pathlib import Path
import sys

root_folder = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_folder))
import gui
import main as backend


csv_path = root_folder / "expenses.csv"
original_csv = csv_path.read_bytes()
chart_paths = [root_folder / "charts" / "category_expenses.png",
               root_folder / "charts" / "monthly_expenses.png"]
created_charts = []
root = None

try:
    root = gui.tk.Tk()
    root.withdraw()
    app = gui.ExpenseTrackerApp(root)
    assert len(app.transactions) == 1  # Existing record was loaded, not replaced.
    assert app.summary_values["TOTAL INCOME"].cget("text") == "₹200,000.00"

    # Adding a positive expense must persist, update the tables/cards, and draw charts.
    app.type_var.set("Expense")
    app.amount_var.set("500")
    app.category_var.set("Food")
    app.description_var.set("UI test lunch")
    app.date_var.set("12-11-2026")
    app.add_transaction()
    root.update_idletasks()
    assert len(app.transactions) == 2
    assert app.summary_values["TOTAL EXPENSES"].cget("text") == "₹500.00"
    assert app.summary_values["CURRENT BALANCE"].cget("text") == "₹199,500.00"
    assert len(app.tree.get_children()) == 2
    assert len(app.month_tree.get_children()) == 1
    assert all(len(frame.winfo_children()) >= 2 for frame in app.chart_frames.values())
    for path in chart_paths:
        assert path.exists() and path.stat().st_size > 0
        created_charts.append(path)

    # Adding income uses the same CSV record structure and refresh path.
    app.type_var.set("Income")
    app.amount_var.set("25000")
    app.category_var.set("Part-time work")
    app.description_var.set("UI test income")
    app.date_var.set("13-11-2026")
    app.add_transaction()
    root.update_idletasks()
    assert len(app.transactions) == 3
    assert app.summary_values["TOTAL INCOME"].cget("text") == "₹225,000.00"
    assert len(list(csv.DictReader(csv_path.open(newline="", encoding="utf-8")))) == 3

    # Invalid amount shows a message and does not append a record.
    messages = []
    gui.messagebox.showerror = lambda *args, **kwargs: messages.append(args)
    before_count = len(app.transactions)
    app.amount_var.set("not-a-number")
    app.add_transaction()
    assert messages and len(app.transactions) == before_count
    print("PASS: Tkinter dashboard, existing CSV load, income/expense saves, live summaries, and charts")
finally:
    if root is not None:
        root.destroy()
    csv_path.write_bytes(original_csv)
    for path in created_charts:
        path.unlink(missing_ok=True)
