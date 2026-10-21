"""Reference-inspired single-page Tkinter interface for ChemMatrix."""

import sys
import tkinter as tk
from tkinter import ttk

from .explanation import (matrix_text, model_text, solution_text,
                          system_headers, verification_text, worked_solution)
from .parser import EquationError
from .solver import balance, format_equation


COMMON_EQUATIONS = (
    "C3H8 + O2 -> CO2 + H2O",
    "Fe + O2 -> Fe2O3",
    "Ca(OH)2 + HCl -> CaCl2 + H2O",
    "Al + H2SO4 -> Al2(SO4)3 + H2",
    "KClO3 -> KCl + O2",
    "H2 + O2 -> H2O",
    "N2 + H2 -> NH3",
    "CH4 + O2 -> CO2 + H2O",
    "C2H5OH + O2 -> CO2 + H2O",
    "CaCO3 -> CaO + CO2",
    "Na + Cl2 -> NaCl",
)


class DerivationView(ttk.Frame):
    """Scrollable derivation cards with a hidden selectable transcript."""

    def __init__(self, parent):
        super().__init__(parent, style="Solution.TFrame")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, background="#f3f8f6", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=vertical.set)
        self.inner = tk.Frame(self.canvas, background="#f3f8f6")
        self.inner.columnconfigure(0, weight=1)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_inner)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.text = tk.Text(self, height=1, width=1)
        self.text.place(x=-100, y=-100)

    def _update_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_inner(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def _on_mousewheel(self, event):
        if self.winfo_exists():
            self.canvas.yview_scroll(-1 * (event.delta // 120 or -1), "units")

    def _transcript(self, value):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.configure(state="disabled")

    def _section(self, title, body):
        section = tk.Frame(self.inner, background="#ffffff", highlightbackground="#dce9e5",
                           highlightthickness=1, padx=20, pady=16)
        section.grid(row=self.inner.grid_size()[1], column=0, sticky="ew", pady=(0, 12))
        section.columnconfigure(0, weight=1)
        tk.Label(section, text=title.upper(), background="#ffffff", foreground="#197568",
                 font=("Menlo", 9, "bold"), anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(section, text=body, background="#ffffff", foreground="#365b56",
                 font=("Menlo", 10), justify="left", anchor="w").grid(
                     row=1, column=0, sticky="w", pady=(9, 0))

    def _step_card(self, number, step, headers):
        card = tk.Frame(self.inner, background="#f8fbfa", highlightbackground="#d9e7e3",
                        highlightthickness=1, padx=20, pady=16)
        card.grid(row=self.inner.grid_size()[1], column=0, sticky="ew", pady=(0, 12))
        card.columnconfigure(1, weight=1)
        tk.Label(card, text=f"{number:02d}", background="#e3f2ee", foreground="#197568",
                 font=("Menlo", 9, "bold"), padx=8, pady=5).grid(
                     row=0, column=0, rowspan=2, sticky="n", padx=(0, 16))
        label = "INITIAL MATRIX" if step.kind == "initial" else f"OPERATION {number - 1}"
        tk.Label(card, text=label, background="#f8fbfa", foreground="#78908c",
                 font=("Menlo", 8, "bold"), anchor="w").grid(row=0, column=1, sticky="w")
        tk.Label(card, text=step.description, background="#f8fbfa", foreground="#173c39",
                 font=("Menlo", 10), anchor="w").grid(row=1, column=1, sticky="w", pady=(7, 0))
        tk.Label(card, text=matrix_text(step.matrix, headers=headers), background="#f8fbfa", foreground="#173c39",
                 font=("Menlo", 10), justify="left", anchor="e").grid(
                     row=0, column=2, rowspan=2, sticky="e", padx=(18, 0))

    def set_solution(self, result):
        transcript = worked_solution(result)
        self._transcript(transcript)
        for child in self.inner.winfo_children():
            child.destroy()
        self._section("Chemical balancing model", model_text(result))
        heading = tk.Frame(self.inner, background="#f3f8f6")
        heading.grid(row=self.inner.grid_size()[1], column=0, sticky="ew", pady=(6, 12))
        tk.Label(heading, text="GAUSS-JORDAN ELIMINATION", background="#f3f8f6",
                 foreground="#197568", font=("Menlo", 9, "bold")).pack(side="left")
        tk.Label(heading, text=f"{len(result.reduction.steps)} steps", background="#e8f1ef",
                 foreground="#56716c", font=("Menlo", 9), padx=9, pady=4).pack(side="right")
        headers = system_headers(result)
        for number, step in enumerate(result.reduction.steps, start=1):
            self._step_card(number, step, headers)
        self._section("Solution", solution_text(result))
        self._section("Verification", verification_text(result))
        self.canvas.yview_moveto(0)
        self._update_scroll_region()

    def set(self, value):
        """Keep the existing view contract for clearing the result."""
        self._transcript(value)
        for child in self.inner.winfo_children():
            child.destroy()
        self._update_scroll_region()


class ChemMatrixApp(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=0, style="App.TFrame")
        self.root = root
        self.result = None
        root.title("ChemMatrix - Linear Algebra Chemical Balancer")
        root.geometry("1180x900")
        root.minsize(780, 620)
        self._configure_styles(root)
        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_header()
        self._build_workspace()
        self.input_var.set(COMMON_EQUATIONS[0])
        self.solve()
        self.equation_entry.focus_set()

    def _configure_styles(self, root):
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f3f8f6")
        style.configure("Page.TFrame", background="#f3f8f6")
        style.configure("Card.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("Solution.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("Title.TLabel", background="#f3f8f6", foreground="#123d39",
                        font=("Helvetica", 31, "bold"))
        style.configure("Eyebrow.TLabel", background="#f3f8f6", foreground="#197568",
                        font=("Menlo", 10, "bold"))
        style.configure("Subtitle.TLabel", background="#f3f8f6", foreground="#708783",
                        font=("Helvetica", 13))
        style.configure("Card.TLabel", background="#ffffff", foreground="#536b67",
                        font=("Helvetica", 10, "bold"))
        style.configure("Helper.TLabel", background="#ffffff", foreground="#8a9c98",
                        font=("Helvetica", 10))
        style.configure("Section.TLabel", background="#f3f8f6", foreground="#173c39",
                        font=("Helvetica", 15, "bold"))
        style.configure("Meta.TLabel", background="#f3f8f6", foreground="#78908c",
                        font=("Menlo", 9))
        style.configure("Primary.TButton", background="#167766", foreground="#ffffff",
                        padding=(18, 11), font=("Helvetica", 10, "bold"))
        style.map("Primary.TButton", background=[("active", "#0f6457")])
        style.configure("Quiet.TButton", background="#ffffff", foreground="#536b67",
                        padding=(18, 11), font=("Helvetica", 10, "bold"))
        style.configure("Equation.TCombobox", fieldbackground="#ffffff", background="#ffffff",
                        foreground="#395b56", padding=8)

    def _build_header(self):
        header = tk.Frame(self, bg="#ffffff", height=68, highlightbackground="#dfeae7",
                          highlightthickness=1)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.columnconfigure(1, weight=1)
        logo = tk.Label(header, text="CM", bg="#167766", fg="#ffffff",
                        font=("Helvetica", 12, "bold"), width=4, height=2)
        logo.grid(row=0, column=0, padx=(28, 10), pady=10)
        tk.Label(header, text="ChemMatrix", bg="#ffffff", fg="#173c39",
                 font=("Helvetica", 15, "bold")).grid(row=0, column=1, sticky="w")
        tk.Frame(header, bg="#d8e5e1", width=1, height=22).grid(row=0, column=2, padx=16)
        tk.Label(header, text="Linear algebra balancer", bg="#ffffff", fg="#7a8e8a",
                 font=("Helvetica", 11)).grid(row=0, column=3, sticky="w")
        tk.Label(header, text="●  EXACT ARITHMETIC", bg="#ffffff", fg="#708783",
                 font=("Menlo", 9, "bold")).grid(row=0, column=4, padx=(20, 30), sticky="e")

    def _build_workspace(self):
        page = ttk.Frame(self, padding=(56, 42, 56, 0), style="Page.TFrame")
        page.grid(row=1, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(4, weight=1)

        hero = ttk.Frame(page, style="Page.TFrame")
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        hero.columnconfigure(0, weight=1)
        ttk.Label(hero, text="EQUATION WORKSPACE", style="Eyebrow.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12))
        ttk.Label(hero, text="Balance with confidence.", style="Title.TLabel").grid(
            row=1, column=0, sticky="w")
        ttk.Label(hero, text="See every conservation constraint, row operation, and verification behind the result.",
                  style="Subtitle.TLabel").grid(row=2, column=0, sticky="w", pady=(10, 0))
        common = ttk.Frame(hero, style="Page.TFrame")
        common.grid(row=0, column=1, rowspan=3, sticky="e", padx=(30, 0))
        ttk.Label(common, text="Common equations", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self.common_choice = ttk.Combobox(common, state="readonly", values=COMMON_EQUATIONS,
                                          width=34, style="Equation.TCombobox")
        self.common_choice.pack(fill="x")
        self.common_choice.current(0)
        self.common_choice.bind("<<ComboboxSelected>>", self.load_common_equation)

        card = ttk.Frame(page, padding=(30, 25, 30, 24), style="Card.TFrame")
        card.grid(row=1, column=0, sticky="ew", pady=(0, 28))
        card.columnconfigure(0, weight=1)
        ttk.Label(card, text="Unbalanced equation", style="Card.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        self.input_var = tk.StringVar()
        self.equation_entry = tk.Entry(card, textvariable=self.input_var, font=("Menlo", 13),
                                       bg="#ffffff", fg="#234844", relief="solid", borderwidth=1,
                                       highlightthickness=1, highlightcolor="#167766",
                                       highlightbackground="#d4e2df", insertbackground="#167766")
        self.equation_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), ipady=10)
        self.balance_button = ttk.Button(card, text="Balance equation", style="Primary.TButton",
                                         command=self.solve)
        self.balance_button.grid(row=1, column=1, padx=(0, 12))
        self.clear_button = ttk.Button(card, text="Clear", style="Quiet.TButton", command=self.clear)
        self.clear_button.grid(row=1, column=2)
        ttk.Label(card, text="Use element symbols with standard numbers. Type -> or = for the reaction arrow.",
                  style="Helper.TLabel").grid(row=2, column=0, columnspan=3, sticky="w", pady=(12, 0))
        self.equation_entry.bind("<Return>", lambda event: self.solve())

        result_bar = ttk.Frame(page, style="Page.TFrame")
        result_bar.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        result_bar.columnconfigure(0, weight=1)
        self.result_var = tk.StringVar(value="Ready to balance.")
        ttk.Label(result_bar, textvariable=self.result_var, style="Section.TLabel").grid(
            row=0, column=0, sticky="w")
        self.method_badge = tk.Label(result_bar, text="METHOD: GAUSS-JORDAN ELIMINATION",
                                     background="#e3f2ee", foreground="#197568",
                                     font=("Menlo", 9, "bold"), padx=10, pady=5)
        self.method_badge.grid(row=0, column=1, padx=(12, 10), sticky="e")
        self.copy_button = ttk.Button(result_bar, text="Copy solution", style="Quiet.TButton",
                                      command=self.copy_solution, state="disabled")
        self.copy_button.grid(row=0, column=2, sticky="e")

        derivation = ttk.Frame(page, style="Page.TFrame")
        derivation.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(derivation, text="FULL DERIVATION", style="Eyebrow.TLabel").pack(side="left")
        self.operation_count = tk.StringVar(value="")
        ttk.Label(derivation, textvariable=self.operation_count, style="Meta.TLabel").pack(side="right")

        self.solution_view = DerivationView(page)
        self.solution_view.grid(row=4, column=0, sticky="nsew")
        self.input_var.trace_add("write", self._invalidate)

    def _invalidate(self, *_):
        if self.result is not None:
            self.result = None
            self.copy_button.configure(state="disabled")
            self.operation_count.set("")
            self.result_var.set("Equation changed - select Balance to rebuild the matrix.")
            self.solution_view.set("")

    def clear(self):
        self.input_var.set("")
        self.solution_view.set("")
        self.operation_count.set("")
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
            self.operation_count.set("")
            self.result_var.set(f"Check the equation: {error}")
            self.solution_view.set("")
            return
        self.result = result
        self.result_var.set(format_equation(result.equation, result.coefficients)
                            if result.coefficients else result.message)
        self.operation_count.set(f"{len(result.reduction.steps) - 1} ROW OPERATIONS")
        self.solution_view.set_solution(result)
        self.copy_button.configure(state="normal")

    def copy_solution(self):
        if self.result:
            self.root.clipboard_clear()
            self.root.clipboard_append(worked_solution(self.result))
            self.result_var.set("Complete worked solution copied.")


def main():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    ChemMatrixApp(root)
    root.mainloop()