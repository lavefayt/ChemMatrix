"""Construct Ax=0, derive a balance, and verify it by counting atoms."""

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from math import gcd, lcm
from typing import Literal

from .matrix import Matrix, Reduction, rref
from .parser import Equation, parse_equation


Status = Literal["balanced", "inconsistent", "no_positive", "multiple_free"]


@dataclass(frozen=True)
class AtomCount:
    element: str
    reactants: int
    products: int

    @property
    def matches(self) -> bool:
        return self.reactants == self.products


@dataclass(frozen=True)
class BalanceResult:
    equation: Equation
    matrix: Matrix                     # A0 (homogeneous, m x n): A0 x0 = 0
    normalized: Matrix                 # [A | b] after fixing x1 = 1 (m x n)
    reduction: Reduction               # Gauss-Jordan on [A | b]
    status: Status
    solution: tuple[Fraction, ...] | None      # (1, x2, ..., xn) before clearing fractions
    coefficients: tuple[int, ...] | None
    message: str


def build_matrix(equation: Equation) -> Matrix:
    split = len(equation.reactants)
    return tuple(tuple(Fraction(c.atoms.get(element, 0) * (1 if i < split else -1))
                       for i, c in enumerate(equation.compounds))
                 for element in equation.elements)


def build_normalized_system(matrix: Matrix) -> Matrix:
    """Fix x1 = 1: move column 1 of A0 to the right-hand side, b = -(column 1)."""
    return tuple(row[1:] + (-row[0],) for row in matrix)


def normalize_coefficients(vector) -> tuple[int, ...]:
    """Orient, clear denominators, and remove the common integer factor."""
    values = tuple(map(Fraction, vector))
    if not values or any(value == 0 for value in values):
        raise ValueError("Every compound must have a strictly positive coefficient.")
    if all(value < 0 for value in values):
        values = tuple(-value for value in values)
    if any(value < 0 for value in values):
        raise ValueError("The solution requires mixed signs on the specified sides.")
    denominator = lcm(*(value.denominator for value in values))
    integers = tuple(int(value * denominator) for value in values)
    divisor = reduce(gcd, integers)
    return tuple(value // divisor for value in integers)


def verify_atoms(equation: Equation, coefficients) -> tuple[AtomCount, ...]:
    coefficients = tuple(coefficients)
    if len(coefficients) != len(equation.compounds) or any(
        type(c) is not int or c <= 0 for c in coefficients
    ):
        raise ValueError("Enter one positive whole-number coefficient per compound.")
    split = len(equation.reactants)
    return tuple(AtomCount(element,
                           sum(c.atoms.get(element, 0) * k for c, k in
                               zip(equation.reactants, coefficients[:split])),
                           sum(c.atoms.get(element, 0) * k for c, k in
                               zip(equation.products, coefficients[split:])))
                 for element in equation.elements)


def balance(text: str) -> BalanceResult:
    equation = parse_equation(text)
    matrix = build_matrix(equation)
    normalized = build_normalized_system(matrix)
    reduction = rref(normalized, pivot_columns=len(equation.compounds) - 1)
    solution = coefficients = None
    if not reduction.consistent:
        status = "inconsistent"
        message = "Fixing x1 = 1 gives an inconsistent system. No balance includes all listed compounds."
    elif reduction.free_columns:
        status = "multiple_free"
        message = ("Free variables remain after fixing x1 = 1. The general solution is shown; "
                   "ChemMatrix does not automatically choose a balance for this system.")
    else:
        solution = (Fraction(1),) + tuple(reduction.matrix[row][-1] for row in range(reduction.rank))
        try:
            coefficients = normalize_coefficients(solution)
        except ValueError as error:
            status, message = "no_positive", str(error)
        else:
            status = "balanced"
            message = "Balanced with the smallest positive whole-number coefficients."
            assert all(count.matches for count in verify_atoms(equation, coefficients))
    return BalanceResult(equation, matrix, normalized, reduction, status,
                         solution, coefficients, message)


def format_equation(equation: Equation, coefficients) -> str:
    terms = [f"{k if k != 1 else ''}{c.formula}" for c, k in zip(equation.compounds, coefficients)]
    split = len(equation.reactants)
    return " + ".join(terms[:split]) + " -> " + " + ".join(terms[split:])