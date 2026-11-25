"""Tkinter dashboard for the Personal Expense Tracker."""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import main as backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


BG = "#f4f6fb"
WHITE = "#ffffff"
NAVY = "#202847"
MUTED = "#77809a"
BLUE = "#5268e8"
PURPLE = "#7655d8"
GREEN = "#15966a"
RED = "#d65365"
LINE = "#e8ebf3"


class ExpenseTrackerApp:
    """Keep the simple UI state and connect buttons to backend functions."""

    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("1280x900")
        self.root.minsize(940, 680)
        self.root.configure(bg=BG)
        self.transactions = backend.load_transactions()
        self.summary_values = {}
        self.chart_frames = {}
        self._configure_styles()
        self._build_layout()
        self.refresh_dashboard()

    def _configure_styles(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                         foreground=NAVY, rowheight=34, borderwidth=0,
                         font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#f7f8fc", foreground=MUTED,
                         font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#e9edff")],
                  foreground=[("selected", NAVY)])
        style.configure("TCombobox", padding=8, font=("Segoe UI", 10))
        style.configure("TEntry", padding=9, font=("Segoe UI", 10))
        style.configure("Horizontal.TProgressbar", troughcolor="#edf0f7",
                         background=BLUE, bordercolor="#edf0f7", lightcolor=BLUE,
                         darkcolor=BLUE)

    def _build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=NAVY, width=215)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="◈  SPENDWISE", bg=NAVY, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(28, 7))
        tk.Label(self.sidebar, text="PERSONAL FINANCE", bg=NAVY, fg="#aab3d2",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(0, 30))
        self.nav_buttons = []
        for label, section in [("▦   Dashboard", "top"), ("＋   Add transaction", "add"),
                               ("☷   Transactions", "transactions"), ("◔   Analytics", "analytics")]:
            button = tk.Button(self.sidebar, text=label, anchor="w", relief="flat",
                               borderwidth=0, bg=NAVY, fg="#d1d6e7",
                               activebackground="#303a62", activeforeground="white",
                               font=("Segoe UI", 10), padx=18, pady=13,
                               command=lambda target=section: self.navigate(target))
            button.pack(fill="x", padx=11, pady=3)
            self.nav_buttons.append(button)
        tk.Label(self.sidebar, text="CSV backed • Local app", bg=NAVY, fg="#aab3d2",
                 font=("Segoe UI", 9)).pack(side="bottom", anchor="w", padx=23, pady=22)

        main_area = tk.Frame(self.root, bg=BG)
        main_area.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(main_area, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_area, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.content = tk.Frame(self.canvas, bg=BG, padx=30, pady=24)
        self.content_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_content)
        self.canvas.bind_all("<MouseWheel>", self._mousewheel)

        self._build_header()
        self._build_summary_cards()
        self._build_add_form()
        self._build_transaction_table()
        self._build_analytics()
        self.status_label = tk.Label(self.content, text="", bg=BG, fg=MUTED,
                                     font=("Segoe UI", 9), anchor="w")
        self.status_label.grid(row=7, column=0, sticky="ew", pady=(0, 14))

    def _update_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event):
        self.canvas.itemconfigure(self.content_window, width=event.width)

    def _mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_header(self):
        header = tk.Frame(self.content, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        header.columnconfigure(0, weight=1)
        tk.Label(header, text="Personal Expense Tracker", bg=BG, fg=NAVY,
                 font=("Segoe UI", 23, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(header, text="Track your income, expenses and spending habits",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(4, 0))
        tk.Label(header, text=datetime.now().strftime("%A, %d %B %Y"), bg=BG,
                 fg=MUTED, font=("Segoe UI", 9)).grid(row=0, column=1, rowspan=2, sticky="e", padx=7)

    def _section_title(self, parent, title, subtitle=None):
        tk.Label(parent, text=title, bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(parent, text=subtitle, bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

    def _build_summary_cards(self):
        row = tk.Frame(self.content, bg=BG)
        row.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        for column in range(4):
            row.columnconfigure(column, weight=1, uniform="summary")
        definitions = [
            ("TOTAL INCOME", "₹0.00", GREEN),
            ("TOTAL EXPENSES", "₹0.00", RED),
            ("CURRENT BALANCE", "₹0.00", BLUE),
            ("TRANSACTIONS", "0", PURPLE),
        ]
        for index, (title, value, accent) in enumerate(definitions):
            card = tk.Frame(row, bg=WHITE, padx=18, pady=17,
                            highlightbackground=LINE, highlightthickness=1)
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 7, 7 if index < 3 else 0))
            tk.Label(card, text=title, bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            value_label = tk.Label(card, text=value, bg=WHITE, fg=accent,
                                   font=("Segoe UI", 19, "bold"))
            value_label.pack(anchor="w", pady=(10, 0))
            self.summary_values[title] = value_label

    def _build_add_form(self):
        self.form_section = tk.Frame(self.content, bg=WHITE, padx=21, pady=19,
                                     highlightbackground=LINE, highlightthickness=1)
        self.form_section.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        self._section_title(self.form_section, "Add transaction", "Record income or an expense")
        form = tk.Frame(self.form_section, bg=WHITE)
        form.pack(fill="x", pady=(17, 6))
        for column in range(3):
            form.columnconfigure(column, weight=1, uniform="form")
        self.type_var = tk.StringVar(value="Expense")
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.now().strftime(backend.DATE_FORMAT))
        self.category_label = None
        self._form_field(form, 0, 0, "Type", "combo", textvariable=self.type_var,
                         values=["Income", "Expense"], state="readonly")
        self._form_field(form, 0, 1, "Amount (₹)", "entry", textvariable=self.amount_var)
        category_control = self._form_field(form, 0, 2, "Category", "combo",
                                             textvariable=self.category_var,
                                             values=backend.CATEGORIES, state="readonly")
        self._form_field(form, 1, 0, "Description", "entry", textvariable=self.description_var)
        self._form_field(form, 1, 1, "Date (DD-MM-YYYY)", "entry", textvariable=self.date_var)
        self.category_control = category_control
        self.type_var.trace_add("write", self._update_category_label)
        actions = tk.Frame(self.form_section, bg=WHITE)
        actions.pack(fill="x", pady=(7, 0))
        tk.Button(actions, text="＋  Add transaction", command=self.add_transaction,
                  bg=BLUE, fg=WHITE, activebackground="#4157d2", activeforeground=WHITE,
                  relief="flat", cursor="hand2", padx=18, pady=10,
                  font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(actions, text="Dates use day-month-year format", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=13)

    def _form_field(self, parent, row, column, title, widget_type, **options):
        wrapper = tk.Frame(parent, bg=WHITE)
        wrapper.grid(row=row, column=column, sticky="ew", padx=(0, 14), pady=(12, 0))
        label = tk.Label(wrapper, text=title, bg=WHITE, fg="#505a73",
                         font=("Segoe UI", 9, "bold"))
        label.pack(anchor="w", pady=(0, 5))
        widget = ttk.Entry(wrapper, **options) if widget_type == "entry" else ttk.Combobox(wrapper, **options)
        widget.pack(fill="x")
        if title == "Category":
            self.category_label = label
        return widget

    def _update_category_label(self, *_args):
        if not self.category_label:
            return
        is_income = self.type_var.get() == "Income"
        self.category_label.configure(text="Source" if is_income else "Category")
        self.category_control.configure(values=[] if is_income else backend.CATEGORIES,
                                        state="normal" if is_income else "readonly")

    def _build_transaction_table(self):
        self.table_section = tk.Frame(self.content, bg=WHITE, padx=21, pady=19,
                                      highlightbackground=LINE, highlightthickness=1)
        self.table_section.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        heading = tk.Frame(self.table_section, bg=WHITE)
        heading.pack(fill="x", pady=(0, 13))
        self._section_title(heading, "Transaction history", "Your latest records from expenses.csv")
        self.tree = ttk.Treeview(self.table_section,
                                 columns=("date", "type", "category", "description", "amount"),
                                 show="headings", height=7)
        labels = {"date": "DATE", "type": "TYPE", "category": "CATEGORY",
                  "description": "DESCRIPTION", "amount": "AMOUNT"}
        for key, label in labels.items():
            self.tree.heading(key, text=label)
        self.tree.column("date", width=120, minwidth=100, anchor="w")
        self.tree.column("type", width=100, minwidth=85, anchor="w")
        self.tree.column("category", width=150, minwidth=100, anchor="w")
        self.tree.column("description", width=330, minwidth=130, anchor="w")
        self.tree.column("amount", width=140, minwidth=110, anchor="e")
        self.tree.tag_configure("Income", foreground=GREEN)
        self.tree.tag_configure("Expense", foreground=RED)
        self.tree.pack(fill="x")

    def _build_analytics(self):
        self.analytics_section = tk.Frame(self.content, bg=BG)
        self.analytics_section.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        self.analytics_section.columnconfigure(0, weight=1, uniform="analytics")
        self.analytics_section.columnconfigure(1, weight=1, uniform="analytics")
        self.category_section = tk.Frame(self.analytics_section, bg=WHITE, padx=20, pady=19,
                                         highlightbackground=LINE, highlightthickness=1)
        self.category_section.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._section_title(self.category_section, "Category summary", "Expense totals by category")
        self.category_summary_frame = tk.Frame(self.category_section, bg=WHITE)
        self.category_summary_frame.pack(fill="x", pady=(15, 0))
        self.month_section = tk.Frame(self.analytics_section, bg=WHITE, padx=20, pady=19,
                                      highlightbackground=LINE, highlightthickness=1)
        self.month_section.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._section_title(self.month_section, "Monthly analysis", "Income, expenses and balance")
        self.month_tree = ttk.Treeview(self.month_section, columns=("month", "income", "expense", "balance"),
                                       show="headings", height=6)
        for key, title in [("month", "MONTH"), ("income", "INCOME"),
                           ("expense", "EXPENSES"), ("balance", "BALANCE")]:
            self.month_tree.heading(key, text=title)
        self.month_tree.column("month", width=95, anchor="w")
        for key in ("income", "expense", "balance"):
            self.month_tree.column(key, width=115, anchor="e")
        self.month_tree.pack(fill="x", pady=(15, 0))

        charts_header = tk.Frame(self.content, bg=BG)
        charts_header.grid(row=5, column=0, sticky="ew", pady=(1, 12))
        tk.Label(charts_header, text="Spending charts", bg=BG, fg=NAVY,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        charts_row = tk.Frame(self.content, bg=BG)
        charts_row.grid(row=6, column=0, sticky="ew", pady=(0, 16))
        charts_row.columnconfigure(0, weight=1, uniform="charts")
        charts_row.columnconfigure(1, weight=1, uniform="charts")
        for column, name, title in [(0, "category", "Expenses by category"),
                                    (1, "monthly", "Monthly income and expenses")]:
            chart_frame = tk.Frame(charts_row, bg=WHITE, padx=10, pady=10,
                                   highlightbackground=LINE, highlightthickness=1)
            chart_frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8,
                                                                     8 if column == 0 else 0))
            tk.Label(chart_frame, text=title, bg=WHITE, fg=NAVY,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=7, pady=(2, 0))
            self.chart_frames[name] = chart_frame

    def navigate(self, section):
        targets = {"top": self.content, "add": self.form_section,
                   "transactions": self.table_section, "analytics": self.analytics_section}
        self.root.update_idletasks()
        target_y = targets[section].winfo_y()
        total_height = max(1, self.content.winfo_height())
        self.canvas.yview_moveto(target_y / total_height)
        if section == "add":
            self.amount_var.set("")

    def add_transaction(self):
        try:
            amount = float(self.amount_var.get().strip())
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a number greater than zero.", parent=self.root)
            return
        category = self.category_var.get().strip()
        description = self.description_var.get().strip()
        date_text = self.date_var.get().strip()
        if not category:
            messagebox.showerror("Missing category", "Enter a category or income source.", parent=self.root)
            return
        if not description:
            messagebox.showerror("Missing description", "Enter a short description.", parent=self.root)
            return
        try:
            datetime.strptime(date_text, backend.DATE_FORMAT)
        except ValueError:
            messagebox.showerror("Invalid date", "Use a valid date in DD-MM-YYYY format.", parent=self.root)
            return

        transaction = {"date": date_text, "type": self.type_var.get(),
                       "category": category, "description": description, "amount": amount}
        if not backend.save_transaction(transaction):
            messagebox.showerror("Save failed", "The transaction could not be saved to expenses.csv.", parent=self.root)
            return
        self.transactions.append(transaction)
        self.amount_var.set("")
        self.description_var.set("")
        self.category_var.set("")
        self.date_var.set(datetime.now().strftime(backend.DATE_FORMAT))
        self.status_label.configure(text="Transaction saved to expenses.csv.", fg=GREEN)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        totals = backend.calculate_totals(self.transactions)
        self.summary_values["TOTAL INCOME"].configure(text=f"₹{totals['income']:,.2f}")
        self.summary_values["TOTAL EXPENSES"].configure(text=f"₹{totals['expenses']:,.2f}")
        self.summary_values["CURRENT BALANCE"].configure(text=f"₹{totals['balance']:,.2f}")
        self.summary_values["TRANSACTIONS"].configure(text=str(len(self.transactions)))
        self._refresh_transaction_table()
        self._refresh_category_summary()
        self._refresh_monthly_table()
        self._refresh_charts()
        if any(item["type"] == "Expense" for item in self.transactions):
            backend.generate_charts(self.transactions)

    def _refresh_transaction_table(self):
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        for item in reversed(self.transactions):
            self.tree.insert("", "end", values=(item["date"], item["type"], item["category"],
                                                   item["description"], f"₹{item['amount']:,.2f}"),
                             tags=(item["type"],))

    def _refresh_category_summary(self):
        for widget in self.category_summary_frame.winfo_children():
            widget.destroy()
        totals = backend.get_category_totals(self.transactions)
        if not totals:
            tk.Label(self.category_summary_frame, text="No expenses recorded yet.", bg=WHITE,
                     fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=10)
            return
        highest = max(totals, key=totals.get)
        max_value = max(totals.values())
        for category, total in sorted(totals.items(), key=lambda pair: pair[1], reverse=True):
            row = tk.Frame(self.category_summary_frame, bg=WHITE)
            row.pack(fill="x", pady=6)
            title = category + ("  •  highest" if category == highest else "")
            tk.Label(row, text=title, bg=WHITE, fg=PURPLE if category == highest else NAVY,
                     font=("Segoe UI", 9, "bold" if category == highest else "normal")).pack(side="left")
            tk.Label(row, text=f"₹{total:,.2f}", bg=WHITE, fg=NAVY,
                     font=("Segoe UI", 9, "bold")).pack(side="right")
            bar = ttk.Progressbar(self.category_summary_frame, maximum=max_value, value=total,
                                  style="Horizontal.TProgressbar")
            bar.pack(fill="x", pady=(0, 3))

    def _refresh_monthly_table(self):
        for item_id in self.month_tree.get_children():
            self.month_tree.delete(item_id)
        summary = backend.build_monthly_summary(self.transactions)
        for month, row in summary.iterrows():
            self.month_tree.insert("", "end", values=(month, f"₹{row['Income']:,.2f}",
                                                        f"₹{row['Expense']:,.2f}",
                                                        f"₹{row['Balance']:,.2f}"))
        if not len(summary):
            self.month_tree.insert("", "end", values=("No data", "—", "—", "—"))

    def _refresh_charts(self):
        for chart_frame in self.chart_frames.values():
            for child in chart_frame.winfo_children()[1:]:
                child.destroy()
        categories = backend.get_category_totals(self.transactions)
        category_figure = Figure(figsize=(4.6, 2.6), dpi=90, facecolor=WHITE)
        category_axis = category_figure.add_subplot(111)
        if categories:
            category_axis.bar(list(categories), list(categories.values()), color=BLUE)
            category_axis.set_ylabel("Rupees", fontsize=8)
            category_axis.tick_params(axis="x", labelrotation=25, labelsize=8)
        else:
            category_axis.text(0.5, 0.5, "Add expenses to see category spending",
                               ha="center", va="center", color=MUTED, fontsize=9)
            category_axis.set_xticks([])
            category_axis.set_yticks([])
        category_axis.set_facecolor(WHITE)
        category_figure.tight_layout()
        self._show_figure(self.chart_frames["category"], category_figure)

        monthly_figure = Figure(figsize=(4.6, 2.6), dpi=90, facecolor=WHITE)
        monthly_axis = monthly_figure.add_subplot(111)
        summary = backend.build_monthly_summary(self.transactions)
        if len(summary):
            x_values = list(range(len(summary)))
            monthly_axis.plot(x_values, summary["Income"].tolist(), marker="o", color=GREEN,
                              linewidth=2, label="Income")
            monthly_axis.plot(x_values, summary["Expense"].tolist(), marker="o", color=RED,
                              linewidth=2, label="Expenses")
            monthly_axis.set_xticks(x_values, summary.index.tolist())
            monthly_axis.tick_params(axis="x", labelrotation=20, labelsize=8)
            monthly_axis.legend(frameon=False, fontsize=8)
            monthly_axis.set_ylabel("Rupees", fontsize=8)
        else:
            monthly_axis.text(0.5, 0.5, "Add transactions to see monthly trends",
                              ha="center", va="center", color=MUTED, fontsize=9)
            monthly_axis.set_xticks([])
            monthly_axis.set_yticks([])
        monthly_axis.set_facecolor(WHITE)
        monthly_figure.tight_layout()
        self._show_figure(self.chart_frames["monthly"], monthly_figure)

    def _show_figure(self, parent, figure):
        chart = FigureCanvasTkAgg(figure, master=parent)
        chart.draw()
        chart.get_tk_widget().pack(fill="x", expand=True, pady=(4, 0))


def launch_gui():
    """Create and run the Tkinter application window."""
    root = tk.Tk()
    ExpenseTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
