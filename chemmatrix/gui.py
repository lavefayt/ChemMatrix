"""Single-page Tkinter interface for ChemMatrix."""

import sys
import tkinter as tk
from tkinter import ttk

from .explanation import worked_solution
from .linear import production_result
from .parser import EquationError
from .solver import balance, format_equation


COMMON_EQUATIONS = (
    "C3H8 + O2 -> CO2 + H2O",
    "Fe + O2 -> Fe2O3",
    "Ca(OH)2 + HCl -> CaCl2 + H2O",
    "Al + H2SO4 -> Al2(SO4)3 + H2",
    "KClO3 -> KCl + O2",
)


class TextView(ttk.Frame):
    """Selectable worked solution with vertical and horizontal scrolling."""

    def __init__(self, parent):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.text = tk.Text(self, wrap="none", font=("Consolas", 11), padx=18, pady=16,
                            background="#ffffff", foreground="#183442", relief="flat")
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        horizontal = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

    def set(self, value):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.configure(state="disabled")
        self.text.yview_moveto(0)
        self.text.xview_moveto(0)


class ChemMatrixApp(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=18)
        self.root = root
        self.result = None
        self.production = production_result()
        root.title("ChemMatrix - Linear Algebra Chemical Balancer")
        root.geometry("1120x820")
        root.minsize(780, 600)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#edf3f5")
        style.configure("TLabel", background="#edf3f5", foreground="#183442", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
        style.configure("Result.TLabel", font=("Segoe UI", 15, "bold"), foreground="#08665e")
        style.configure("TButton", padding=(10, 6), font=("Segoe UI", 10))
        style.configure("TNotebook.Tab", padding=(18, 9), font=("Segoe UI", 10))
        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="ChemMatrix", style="Title.TLabel").grid(sticky="w")
        ttk.Label(self, text="Balance atoms, then follow the complete matrix solution.").grid(
            sticky="w", pady=(0, 12))

        self.balancer = ttk.Frame(self)
        self.balancer.grid(row=2, column=0, sticky="nsew")
        self.balancer.columnconfigure(0, weight=1)
        self.balancer.rowconfigure(4, weight=1)
        self._build_balancer()

        self.input_var.set(COMMON_EQUATIONS[0])
        self.solve()
        self.equation_entry.focus_set()

    def _build_balancer(self):
        page = self.balancer
        ttk.Label(page, text="Unbalanced chemical equation").grid(row=0, column=0, sticky="w")
        bar = ttk.Frame(page)
        bar.grid(row=1, column=0, sticky="ew", pady=(5, 8))
        bar.columnconfigure(0, weight=1)
        self.input_var = tk.StringVar()
        self.equation_entry = ttk.Entry(bar, textvariable=self.input_var, font=("Consolas", 13))
        self.equation_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.equation_entry.bind("<Return>", lambda event: self.solve())
        self.balance_button = ttk.Button(bar, text="Balance", command=self.solve)
        self.balance_button.grid(row=0, column=1)
        self.clear_button = ttk.Button(bar, text="Clear", command=self.clear)
        self.clear_button.grid(row=0, column=2, padx=(6, 0))

        choices = ttk.Frame(page)
        choices.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(choices, text="Common equations").pack(side="left", padx=(0, 8))
        self.common_choice = ttk.Combobox(choices, state="readonly", values=COMMON_EQUATIONS, width=42)
        self.common_choice.pack(side="left", fill="x", expand=True)
        self.common_choice.current(0)
        self.common_choice.bind("<<ComboboxSelected>>", self.load_common_equation)
        self.copy_button = ttk.Button(choices, text="Copy solution", command=self.copy_solution, state="disabled")
        self.copy_button.pack(side="right", padx=(8, 0))

        self.result_var = tk.StringVar(value="Ready to balance.")
        ttk.Label(page, textvariable=self.result_var, style="Result.TLabel", wraplength=1000).grid(
            row=3, column=0, sticky="ew", pady=(2, 8))
        self.solution_view = TextView(page)
        self.solution_view.grid(row=4, column=0, sticky="nsew")
        self.input_var.trace_add("write", self._invalidate)

    def _invalidate(self, *_):
        if self.result is not None:
            self.result = None
            self.copy_button.configure(state="disabled")
            self.result_var.set("Equation changed - select Balance to rebuild the matrix.")
            self.solution_view.set("")

    def clear(self):
        self.input_var.set("")
        self.solution_view.set("")
        self.result_var.set("Enter an equation to begin.")
        self.equation_entry.focus_set()

    def load_common_equation(self, _event=None):
        self.input_var.set(self.common_choice.get())
        self.solve()

    def solve(self):
        try:
            result = balance(self.input_var.get())
        except EquationError as error:
            self.result = None
            self.copy_button.configure(state="disabled")
            self.result_var.set(f"Check the equation: {error}")
            self.solution_view.set("")
            return
        self.result = result
        self.result_var.set(format_equation(result.equation, result.coefficients)
                            if result.coefficients else result.message)
        self.solution_view.set(worked_solution(result, self.production))
        self.copy_button.configure(state="normal")

    def copy_solution(self):
        if self.result:
            self.root.clipboard_clear()
            self.root.clipboard_append(worked_solution(self.result, self.production))
            self.result_var.set("Complete worked solution copied.")


def main():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    ChemMatrixApp(root)
    root.mainloop()
