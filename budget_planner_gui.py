import json
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = Path(__file__).with_name("budget_data.json")

DEFAULT_DATA = {
    "income": [],
    "bills": [],
    "goals": [],
    "allocation": {
        "savings": 30,
        "investments": 30,
        "goals": 30,
        "spending": 10,
    },
}


def money(value):
    return f"£{value:,.2f}"


def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                data = json.load(f)
            for key in DEFAULT_DATA:
                if key not in data:
                    data[key] = DEFAULT_DATA[key]
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def months_until(deadline):
    year, month = map(int, deadline.split("-"))
    today = date.today()
    return max(1, (year - today.year) * 12 + (month - today.month))


def monthly_needed(goal):
    remaining = max(0.0, goal["target"] - goal["saved"])
    return remaining / months_until(goal["deadline"])


def parse_deadline(text):
    text = text.strip()
    try:
        year, month = map(int, text.split("-"))
        if not 1 <= month <= 12:
            raise ValueError
        if (year, month) <= (date.today().year, date.today().month):
            raise ValueError
        return f"{year:04d}-{month:02d}"
    except ValueError:
        raise ValueError("Use YYYY-MM with a future month.")


class BudgetPlannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Budget & Financial Planning Tool")
        self.geometry("1100x760")
        self.minsize(1000, 700)

        self.data = load_data()

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.main = ttk.Frame(self, padding=12)
        self.main.pack(fill="both", expand=True)

        left = ttk.Frame(self.main)
        left.pack(side="left", fill="both", expand=True)

        # Income section
        income_frame = ttk.LabelFrame(left, text="Income", padding=10)
        income_frame.pack(fill="x", pady=(0, 10))
        self.income_tree = ttk.Treeview(income_frame, columns=("name", "amount"), show="headings", height=5)
        self.income_tree.heading("name", text="Name")
        self.income_tree.heading("amount", text="Amount")
        self.income_tree.column("name", width=220, anchor="w")
        self.income_tree.column("amount", width=130, anchor="e")
        self.income_tree.pack(fill="x")

        income_form = ttk.Frame(income_frame)
        income_form.pack(fill="x", pady=(8, 0))
        ttk.Label(income_form, text="Name").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=2)
        self.income_name = ttk.Entry(income_form, width=22)
        self.income_name.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(income_form, text="Amount").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=2)
        self.income_amount = ttk.Entry(income_form, width=14)
        self.income_amount.grid(row=0, column=3, sticky="ew")
        ttk.Button(income_form, text="Add Income", command=self.add_income).grid(row=1, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        income_form.columnconfigure(1, weight=1)
        income_form.columnconfigure(3, weight=1)

        # Bills section
        bills_frame = ttk.LabelFrame(left, text="Bills / Commitments", padding=10)
        bills_frame.pack(fill="x", pady=(0, 10))
        self.bill_tree = ttk.Treeview(bills_frame, columns=("name", "amount", "due"), show="headings", height=5)
        self.bill_tree.heading("name", text="Name")
        self.bill_tree.heading("amount", text="Amount")
        self.bill_tree.heading("due", text="Due Day")
        self.bill_tree.column("name", width=190, anchor="w")
        self.bill_tree.column("amount", width=120, anchor="e")
        self.bill_tree.column("due", width=80, anchor="center")
        self.bill_tree.pack(fill="x")

        bills_form = ttk.Frame(bills_frame)
        bills_form.pack(fill="x", pady=(8, 0))
        ttk.Label(bills_form, text="Name").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=2)
        self.bill_name = ttk.Entry(bills_form, width=18)
        self.bill_name.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(bills_form, text="Amount").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=2)
        self.bill_amount = ttk.Entry(bills_form, width=12)
        self.bill_amount.grid(row=0, column=3, sticky="ew", padx=(0, 8))
        ttk.Label(bills_form, text="Due day").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=2)
        self.bill_due = ttk.Entry(bills_form, width=8)
        self.bill_due.grid(row=1, column=1, sticky="w", padx=(0, 8))
        ttk.Button(bills_form, text="Add Bill", command=self.add_bill).grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        bills_form.columnconfigure(1, weight=1)
        bills_form.columnconfigure(3, weight=1)

        # Goals section
        goals_frame = ttk.LabelFrame(left, text="Savings Goals", padding=10)
        goals_frame.pack(fill="x")
        self.goal_tree = ttk.Treeview(goals_frame, columns=("name", "target", "saved", "deadline"), show="headings", height=5)
        self.goal_tree.heading("name", text="Name")
        self.goal_tree.heading("target", text="Target")
        self.goal_tree.heading("saved", text="Saved")
        self.goal_tree.heading("deadline", text="Deadline")
        self.goal_tree.column("name", width=135, anchor="w")
        self.goal_tree.column("target", width=110, anchor="e")
        self.goal_tree.column("saved", width=110, anchor="e")
        self.goal_tree.column("deadline", width=90, anchor="center")
        self.goal_tree.pack(fill="x")

        goals_form = ttk.Frame(goals_frame)
        goals_form.pack(fill="x", pady=(8, 0))
        ttk.Label(goals_form, text="Goal").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=2)
        self.goal_name = ttk.Entry(goals_form, width=18)
        self.goal_name.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        ttk.Label(goals_form, text="Target").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=2)
        self.goal_target = ttk.Entry(goals_form, width=12)
        self.goal_target.grid(row=0, column=3, sticky="ew", padx=(0, 8))

        ttk.Label(goals_form, text="Saved").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=2)
        self.goal_saved = ttk.Entry(goals_form, width=12)
        self.goal_saved.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ttk.Label(goals_form, text="Deadline").grid(row=1, column=2, sticky="w", padx=(0, 6), pady=2)
        self.goal_deadline = ttk.Entry(goals_form, width=12)
        self.goal_deadline.grid(row=1, column=3, sticky="ew")
        ttk.Button(goals_form, text="Add Goal", command=self.add_goal).grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        goals_form.columnconfigure(1, weight=1)
        goals_form.columnconfigure(3, weight=1)

        # Right side panel
        right = ttk.Frame(self.main)
        right.pack(side="right", fill="both", expand=True, padx=(12, 0))

        summary_frame = ttk.LabelFrame(right, text="Summary", padding=10)
        summary_frame.pack(fill="x", pady=(0, 12))
        self.summary_labels = {
            "income": tk.StringVar(value="£0.00"),
            "bills": tk.StringVar(value="£0.00"),
            "surplus": tk.StringVar(value="£0.00"),
            "share": tk.StringVar(value="0%"),
        }
        ttk.Label(summary_frame, text="Income:").grid(row=0, column=0, sticky="w")
        ttk.Label(summary_frame, textvariable=self.summary_labels["income"]).grid(row=0, column=1, sticky="e")
        ttk.Label(summary_frame, text="Bills:").grid(row=1, column=0, sticky="w")
        ttk.Label(summary_frame, textvariable=self.summary_labels["bills"]).grid(row=1, column=1, sticky="e")
        ttk.Label(summary_frame, text="Surplus:").grid(row=2, column=0, sticky="w")
        ttk.Label(summary_frame, textvariable=self.summary_labels["surplus"]).grid(row=2, column=1, sticky="e")
        ttk.Label(summary_frame, text="Bills % of income:").grid(row=3, column=0, sticky="w")
        ttk.Label(summary_frame, textvariable=self.summary_labels["share"]).grid(row=3, column=1, sticky="e")
        summary_frame.columnconfigure(1, weight=1)

        allocation_frame = ttk.LabelFrame(right, text="Allocation", padding=10)
        allocation_frame.pack(fill="x", pady=(0, 12))
        self.alloc_vars = {}
        for idx, key in enumerate(["savings", "investments", "goals", "spending"]):
            ttk.Label(allocation_frame, text=key.capitalize()).grid(row=idx, column=0, sticky="w", padx=(0, 8), pady=2)
            var = tk.StringVar(value=str(self.data["allocation"].get(key, 0)))
            self.alloc_vars[key] = var
            ttk.Entry(allocation_frame, textvariable=var, width=8).grid(row=idx, column=1, sticky="w")
        ttk.Button(allocation_frame, text="Save Allocation", command=self.save_allocation).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        actions_frame = ttk.LabelFrame(right, text="Actions", padding=10)
        actions_frame.pack(fill="x", pady=(0, 12))
        ttk.Button(actions_frame, text="Load Demo Data", command=self.load_demo).pack(fill="x", pady=(0, 6))
        ttk.Button(actions_frame, text="Save Data", command=self.save_current).pack(fill="x", pady=(0, 6))
        ttk.Button(actions_frame, text="Clear Data", command=self.clear_data).pack(fill="x")

        plan_frame = ttk.LabelFrame(right, text="Goal Progress", padding=10)
        plan_frame.pack(fill="both", expand=True)
        self.plan_display = tk.Text(plan_frame, height=18, wrap="word", state="disabled")
        self.plan_display.pack(fill="both", expand=True)

        self.refresh_views()

    def save_current(self):
        self.data["income"] = [
            {"name": row[0], "amount": float(row[1])}
            for row in [tuple(self.income_tree.item(item, "values")) for item in self.income_tree.get_children()]
        ]
        self.data["bills"] = [
            {"name": row[0], "amount": float(row[1]), "due_day": int(row[2])}
            for row in [tuple(self.bill_tree.item(item, "values")) for item in self.bill_tree.get_children()]
        ]
        self.data["goals"] = [
            {"name": row[0], "target": float(row[1]), "saved": float(row[2]), "deadline": row[3]}
            for row in [tuple(self.goal_tree.item(item, "values")) for item in self.goal_tree.get_children()]
        ]
        save_data(self.data)
        self.refresh_views()

    def add_income(self):
        name = self.income_name.get().strip()
        value = self.income_amount.get().strip()
        if not name:
            messagebox.showerror("Missing data", "Please enter an income name.")
            return
        try:
            amount = float(value)
        except ValueError:
            messagebox.showerror("Invalid amount", "Income amount must be a number.")
            return
        self.data["income"].append({"name": name, "amount": round(amount, 2)})
        self.income_name.delete(0, tk.END)
        self.income_amount.delete(0, tk.END)
        save_data(self.data)
        self.refresh_views()

    def add_bill(self):
        name = self.bill_name.get().strip()
        value = self.bill_amount.get().strip()
        due_day = self.bill_due.get().strip()
        if not name:
            messagebox.showerror("Missing data", "Please enter a bill name.")
            return
        try:
            amount = float(value)
            due = int(due_day)
        except ValueError:
            messagebox.showerror("Invalid data", "Amount must be numeric and due day must be a whole number.")
            return
        if not 1 <= due <= 28:
            messagebox.showerror("Invalid due day", "Due day must be between 1 and 28.")
            return
        self.data["bills"].append({"name": name, "amount": round(amount, 2), "due_day": due})
        self.bill_name.delete(0, tk.END)
        self.bill_amount.delete(0, tk.END)
        self.bill_due.delete(0, tk.END)
        save_data(self.data)
        self.refresh_views()

    def add_goal(self):
        name = self.goal_name.get().strip()
        target = self.goal_target.get().strip()
        saved = self.goal_saved.get().strip()
        deadline = self.goal_deadline.get().strip()
        if not name:
            messagebox.showerror("Missing data", "Please enter a goal name.")
            return
        try:
            target_amount = float(target)
            saved_amount = float(saved)
            if target_amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid goal", "Target and saved values must be numbers and target must be greater than zero.")
            return
        try:
            deadline_value = parse_deadline(deadline)
        except ValueError as exc:
            messagebox.showerror("Invalid deadline", str(exc))
            return
        self.data["goals"].append({
            "name": name,
            "target": round(target_amount, 2),
            "saved": round(saved_amount, 2),
            "deadline": deadline_value,
        })
        self.goal_name.delete(0, tk.END)
        self.goal_target.delete(0, tk.END)
        self.goal_saved.delete(0, tk.END)
        self.goal_deadline.delete(0, tk.END)
        save_data(self.data)
        self.refresh_views()

    def save_allocation(self):
        values = {}
        try:
            for key in ("savings", "investments", "goals", "spending"):
                values[key] = int(self.alloc_vars[key].get())
        except ValueError:
            messagebox.showerror("Invalid allocation", "Each allocation must be a whole number.")
            return
        if sum(values.values()) != 100:
            messagebox.showerror("Allocation invalid", f"The total must be 100%. Current total: {sum(values.values())}%.")
            return
        self.data["allocation"] = values
        save_data(self.data)
        self.refresh_views()

    def load_demo(self):
        next_year = date.today().year + 1
        self.data = {
            "income": [{"name": "Salary", "amount": 2100.0}],
            "bills": [
                {"name": "Rent", "amount": 750.0, "due_day": 1},
                {"name": "Council tax", "amount": 120.0, "due_day": 5},
                {"name": "Energy", "amount": 95.0, "due_day": 10},
                {"name": "Phone and broadband", "amount": 45.0, "due_day": 15},
                {"name": "Travel", "amount": 80.0, "due_day": 20},
                {"name": "Subscriptions", "amount": 25.0, "due_day": 25},
            ],
            "goals": [
                {"name": "House deposit", "target": 8000.0, "saved": 1500.0, "deadline": f"{next_year + 1}-06"},
                {"name": "Holiday", "target": 1200.0, "saved": 200.0, "deadline": f"{next_year}-07"},
            ],
            "allocation": {"savings": 30, "investments": 30, "goals": 30, "spending": 10},
        }
        save_data(self.data)
        self.refresh_views()

    def clear_data(self):
        self.data = json.loads(json.dumps(DEFAULT_DATA))
        save_data(self.data)
        self.refresh_views()

    def refresh_views(self):
        self._populate_tree(self.income_tree, self.data["income"], ["name", "amount"], lambda item: (item["name"], money(item["amount"])))
        self._populate_tree(self.bill_tree, self.data["bills"], ["name", "amount", "due_day"], lambda item: (item["name"], money(item["amount"]), item["due_day"]))
        self._populate_tree(self.goal_tree, self.data["goals"], ["name", "target", "saved", "deadline"], lambda item: (item["name"], money(item["target"]), money(item["saved"]), item["deadline"]))

        for key, var in self.alloc_vars.items():
            value = self.data["allocation"].get(key, 0)
            var.set(str(value))

        income = sum(item["amount"] for item in self.data["income"])
        bills = sum(item["amount"] for item in self.data["bills"])
        surplus = income - bills
        self.summary_labels["income"].set(money(income))
        self.summary_labels["bills"].set(money(bills))
        self.summary_labels["surplus"].set(money(surplus))
        self.summary_labels["share"].set(f"{(bills / income * 100):.0f}%" if income > 0 else "0%")

        self._update_goal_plan()

    def _populate_tree(self, tree, items, columns, mapper):
        for child in tree.get_children():
            tree.delete(child)
        for item in items:
            tree.insert("", "end", values=mapper(item))

    def _update_goal_plan(self):
        surplus = sum(item["amount"] for item in self.data["income"]) - sum(item["amount"] for item in self.data["bills"])
        text_lines = []
        if surplus <= 0:
            text_lines.append("No surplus to allocate. Consider reducing bills or increasing income.")
        else:
            alloc = self.data["allocation"]
            pots = {name: surplus * pct / 100 for name, pct in alloc.items()}
            text_lines.append(f"Surplus to allocate: {money(surplus)}")
            for name, pct in alloc.items():
                text_lines.append(f"- {name.capitalize():<12}{pct:>3}%  {money(pots[name])}")

        if self.data["goals"]:
            text_lines.append("")
            text_lines.append("Goal progress:")
            needs = [monthly_needed(g) for g in self.data["goals"]]
            required = sum(needs)
            pot = pots["goals"] if surplus > 0 else 0
            ratio = 1.0 if required == 0 else min(1.0, pot / required)
            for g, need in zip(self.data["goals"], needs):
                funded = need * ratio
                pct_done = (g["saved"] / g["target"] * 100) if g["target"] else 0
                status = "on track" if ratio >= 1 else f"short by {money(need - funded)}/month"
                text_lines.append(
                    f"- {g['name']}: {pct_done:.0f}% saved ({money(g['saved'])} of {money(g['target'])}), by {g['deadline']}"
                )
                text_lines.append(f"  needs {money(need)}/month, funded {money(funded)} - {status}")
        else:
            text_lines.append("")
            text_lines.append("No goals set yet.")

        self.plan_display.config(state="normal")
        self.plan_display.delete("1.0", tk.END)
        self.plan_display.insert("1.0", "\n".join(text_lines))
        self.plan_display.config(state="disabled")


if __name__ == "__main__":
    app = BudgetPlannerApp()
    app.mainloop()
