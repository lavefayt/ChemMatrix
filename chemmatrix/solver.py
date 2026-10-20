"""Construct Ax=0, derive a balance, and verify it by counting atoms."""

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from math import gcd, lcm
from typing import Literal

from .matrix import Matrix, Reduction, rref
from .parser import Equation, parse_equation


Status = Literal["balanced", "zero_only", "no_positive", "multiple_free"]


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
    matrix: Matrix
    reduction: Reduction
    status: Status
    coefficients: tuple[int, ...] | None
    message: str


def build_matrix(equation: Equation) -> Matrix:
    split = len(equation.reactants)
    return tuple(tuple(Fraction(c.atoms.get(element, 0) * (1 if i < split else -1))
                       for i, c in enumerate(equation.compounds))
                 for element in equation.elements)


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
    reduction = rref(matrix)
    basis = reduction.basis
    if not basis:
        status, coefficients = "zero_only", None
        message = "Only x = 0 satisfies this system. No balance includes all listed compounds."
    elif len(basis) > 1:
        status, coefficients = "multiple_free", None
        message = ("Multiple independent free variables remain. The general solution is shown; "
                   "ChemMatrix does not automatically choose a balance for this system.")
    else:
        try:
            coefficients = normalize_coefficients(basis[0])
        except ValueError as error:
            status, coefficients, message = "no_positive", None, str(error)
        else:
            status = "balanced"
            message = "Balanced with the smallest positive whole-number coefficients."
            assert all(count.matches for count in verify_atoms(equation, coefficients))
    return BalanceResult(equation, matrix, reduction, status, coefficients, message)


def format_equation(equation: Equation, coefficients) -> str:
    terms = [f"{k if k != 1 else ''}{c.formula}" for c, k in zip(equation.compounds, coefficients)]
    split = len(equation.reactants)
    return " + ".join(terms[:split]) + " -> " + " + ".join(terms[split:])
