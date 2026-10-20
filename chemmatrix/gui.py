"""Tkinter presentation: all mathematical work lives in independent modules."""

import tkinter as tk
from tkinter import ttk
import sys

from .explanation import (counts_text, matrix_text, model_text, solution_text,
                          verification_text, worked_solution)
from .parser import EquationError, parse_equation
from .practice import EXERCISES, check_answer
from .solver import balance, format_equation


class TextView(ttk.Frame):
    """Selectable read-only text with both scroll directions."""

    def __init__(self, parent):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.text = tk.Text(self, wrap="none", font=("Consolas", 11), padx=16, pady=14,
                            background="#ffffff", foreground="#183442", relief="flat")
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        horizontal = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.set("")

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
        self.step_index = 0
        self.solved = set()
        self.assisted = set()
        self.practice_entries = []
        self.practice_vars = []
        self.practice_ready = False
        root.title("ChemMatrix — Chemical Equation Balancer")
        root.geometry("1120x820")
        root.minsize(800, 650)
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
        ttk.Label(self, text="Balance atoms. Build a matrix. Follow the algebra.").grid(sticky="w", pady=(0, 14))
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=2, column=0, sticky="nsew")
        self.balancer = ttk.Frame(self.tabs, padding=14)
        self.practice = ttk.Frame(self.tabs, padding=14)
        self.tabs.add(self.balancer, text="Balancer", underline=0)
        self.tabs.add(self.practice, text="Practice", underline=0)
        self.tabs.enable_traversal()
        self._build_balancer()
        self._build_practice()
        self.input_var.set("C3H8 + O2 -> CO2 + H2O")
        self.equation_entry.focus_set()

    def _build_balancer(self):
        page = self.balancer
        page.columnconfigure(0, weight=1)
        page.rowconfigure(5, weight=1)
        ttk.Label(page, text="Unbalanced equation (use ->, →, or =)").grid(sticky="w")
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
        self.clear_button.grid(row=0, column=2, padx=6)
        examples = ttk.Frame(page)
        examples.grid(row=2, column=0, sticky="ew")
        ttk.Label(examples, text="Examples:").pack(side="left")
        for label, equation in [("Propane", EXERCISES[5].equation), ("Iron", EXERCISES[3].equation),
                                ("Parentheses", EXERCISES[7].equation)]:
            ttk.Button(examples, text=label, command=lambda eq=equation: self.load_example(eq)).pack(side="left", padx=4)
        self.copy_button = ttk.Button(examples, text="Copy worked solution", command=self.copy_solution, state="disabled")
        self.copy_button.pack(side="right")
        self.result_var = tk.StringVar(value="Enter an equation to begin.")
        self.result_label = ttk.Label(page, textvariable=self.result_var, style="Result.TLabel", wraplength=980)
        self.result_label.grid(row=3, column=0, sticky="ew", pady=(12, 5))
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(page, textvariable=self.status_var, wraplength=980)
        self.status_label.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        page.bind("<Configure>", lambda event: self._wrap_labels(event.width))
        self.views = ttk.Notebook(page)
        self.views.grid(row=5, column=0, sticky="nsew")
        self.model_view = TextView(self.views)
        self.steps_page = ttk.Frame(self.views)
        self.steps_page.columnconfigure(0, weight=1)
        self.steps_page.rowconfigure(1, weight=1)
        self.verify_view = TextView(self.views)
        for frame, label in [(self.model_view, "Model"), (self.steps_page, "Solution Steps"), (self.verify_view, "Verification")]:
            self.views.add(frame, text=label)
        navigation = ttk.Frame(self.steps_page, padding=6)
        navigation.grid(row=0, column=0, sticky="ew")
        self.previous_button = ttk.Button(navigation, text="Previous", command=lambda: self.move_step(-1), state="disabled")
        self.previous_button.pack(side="left")
        self.next_button = ttk.Button(navigation, text="Next", command=lambda: self.move_step(1), state="disabled")
        self.next_button.pack(side="left", padx=6)
        self.step_var = tk.StringVar(value="Balance an equation to see row operations.")
        ttk.Label(navigation, textvariable=self.step_var).pack(side="left", padx=8)
        self.steps_view = TextView(self.steps_page)
        self.steps_view.grid(row=1, column=0, sticky="nsew")
        self.input_var.trace_add("write", self._invalidate)
        self.model_view.set("Enter a neutral equation above, then select Balance.\n\n"
                            "Example: C3H8 + O2 -> CO2 + H2O\n\n"
                            "Use ordinary digits and case-sensitive symbols.\n"
                            "Leave out coefficients, charges, hydrates, and state labels.")

    def _invalidate(self, *_):
        self.result = None
        self.step_index = 0
        self.result_var.set("Ready to balance." if self.input_var.get().strip() else "Enter an equation to begin.")
        self.status_var.set("Balance the current input to enable solution views and copying."
                            if self.input_var.get().strip() else "")
        for view in (self.model_view, self.steps_view, self.verify_view):
            view.set("")
        for button in (self.copy_button, self.previous_button, self.next_button):
            button.configure(state="disabled")
        self.step_var.set("Balance an equation to see row operations.")

    def _wrap_labels(self, width):
        for label in (self.result_label, self.status_label):
            label.configure(wraplength=max(300, width - 32))

    def clear(self):
        self.input_var.set("")
        self.equation_entry.focus_set()

    def load_example(self, equation):
        self.input_var.set(equation)
        self.solve()

    def solve(self):
        try:
            result = balance(self.input_var.get())
        except EquationError as error:
            self._invalidate()
            self.result_var.set("Check your equation")
            self.status_var.set(str(error))
            return
        self.result = result
        self.step_index = 0
        self.result_var.set(format_equation(result.equation, result.coefficients)
                            if result.coefficients else "No single positive balance selected")
        self.status_var.set(result.message)
        self.model_view.set(model_text(result))
        self.verify_view.set(verification_text(result))
        self.copy_button.configure(state="normal")
        self.show_step()

    def show_step(self):
        if self.result is None:
            return
        steps = self.result.reduction.steps
        step = steps[self.step_index]
        self.step_var.set(f"Step {self.step_index + 1} of {len(steps)}")
        self.previous_button.configure(state="normal" if self.step_index else "disabled")
        self.next_button.configure(state="normal" if self.step_index < len(steps) - 1 else "disabled")
        text = step.description + "\n\n" + matrix_text(step.matrix)
        if self.step_index == len(steps) - 1:
            text += "\n\nREDUCED ROW ECHELON FORM\n\n" + solution_text(self.result)
        else:
            text += "\n\nFollow each row operation to reach reduced row echelon form."
        self.steps_view.set(text)

    def move_step(self, offset):
        if self.result:
            self.step_index = min(max(0, self.step_index + offset), len(self.result.reduction.steps) - 1)
            self.show_step()

    def copy_solution(self):
        if self.result:
            self.root.clipboard_clear()
            self.root.clipboard_append(worked_solution(self.result))
            self.status_var.set("Worked solution copied to the clipboard.")

    def _build_practice(self):
        page = self.practice
        page.columnconfigure(0, weight=1)
        page.rowconfigure(5, weight=1)
        top = ttk.Frame(page)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Label(top, text="Choose an exercise:").pack(side="left", padx=(0, 8))
        self.exercise_choice = ttk.Combobox(top, state="readonly", width=47,
                                            values=[f"{e.difficulty} — {e.title}" for e in EXERCISES])
        self.exercise_choice.pack(side="left")
        self.exercise_choice.current(0)
        self.exercise_choice.bind("<<ComboboxSelected>>", lambda event: self.load_exercise())
        self.progress_var = tk.StringVar()
        ttk.Label(page, textvariable=self.progress_var).grid(row=1, column=0, sticky="w", pady=10)
        ttk.Label(page, text="Enter a positive whole-number coefficient for every compound, including 1.").grid(
            row=2, column=0, sticky="w")
        self.coefficient_bar = ttk.Frame(page)
        self.coefficient_bar.grid(row=3, column=0, sticky="ew", pady=12)
        actions = ttk.Frame(page)
        actions.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        self.check_button = ttk.Button(actions, text="Check atom counts", command=self.check_practice)
        self.check_button.pack(side="left")
        self.retry_button = ttk.Button(actions, text="Retry", command=self.retry_practice)
        self.retry_button.pack(side="left", padx=6)
        self.hint_button = ttk.Button(actions, text="Hint", command=self.show_hint)
        self.hint_button.pack(side="left")
        self.reveal_button = ttk.Button(actions, text="Reveal worked solution", command=self.reveal_practice)
        self.reveal_button.pack(side="left", padx=6)
        self.practice_view = TextView(page)
        self.practice_view.grid(row=5, column=0, sticky="nsew")
        self.load_exercise()

    @property
    def exercise_index(self):
        return self.exercise_choice.current()

    def update_progress(self):
        noun = "exercise" if len(self.assisted) == 1 else "exercises"
        self.progress_var.set(f"Session progress: {len(self.solved)} / {len(EXERCISES)} solved independently "
                              f"• {len(self.assisted)} {noun} assisted by hints or reveal")

    def load_exercise(self):
        self.practice_ready = False
        for child in self.coefficient_bar.winfo_children():
            child.destroy()
        self.practice_entries = []
        self.practice_vars = []
        equation = parse_equation(EXERCISES[self.exercise_index].equation)
        for i, compound in enumerate(equation.compounds):
            if i:
                ttk.Label(self.coefficient_bar, text="→" if i == len(equation.reactants) else "+").pack(side="left", padx=5)
            var = tk.StringVar()
            entry = ttk.Entry(self.coefficient_bar, textvariable=var, width=5, font=("Consolas", 12))
            entry.pack(side="left")
            entry.bind("<Return>", lambda event: self.check_practice())
            var.trace_add("write", self._practice_edited)
            self.practice_vars.append(var)
            self.practice_entries.append(entry)
            ttk.Label(self.coefficient_bar, text=compound.formula).pack(side="left", padx=(3, 6))
        self.practice_ready = True
        self.practice_view.set("Enter coefficients and select Check atom counts.\n\n"
                               "Hints and reveals are marked as assisted for this session.")
        self.update_progress()

    def _practice_edited(self, *_):
        if self.practice_ready:
            self.practice_view.set("Answer changed. Select Check atom counts to verify it.")

    def check_practice(self):
        feedback = check_answer(EXERCISES[self.exercise_index], [var.get() for var in self.practice_vars])
        if feedback.status == "correct" and self.exercise_index not in self.assisted:
            self.solved.add(self.exercise_index)
        text = feedback.message
        if feedback.counts:
            text += "\n\n" + counts_text(feedback.counts)
        if self.exercise_index in self.assisted:
            text += "\n\nThis exercise is marked assisted for this session."
        self.practice_view.set(text)
        self.update_progress()

    def retry_practice(self):
        for var in self.practice_vars:
            var.set("")
        self.practice_view.set("Try again. Enter one coefficient per compound.")
        self.practice_entries[0].focus_set()

    def show_hint(self):
        self.assisted.add(self.exercise_index)
        self.practice_view.set("HINT\n\n" + EXERCISES[self.exercise_index].hint)
        self.update_progress()

    def reveal_practice(self):
        self.assisted.add(self.exercise_index)
        self.practice_view.set(worked_solution(balance(EXERCISES[self.exercise_index].equation)))
        self.update_progress()


def main():
    if sys.platform == "win32":
        # Keep Tk's layout and Windows display coordinates consistent at high DPI.
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    ChemMatrixApp(root)
    root.mainloop()
