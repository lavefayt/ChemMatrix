"""Exact 3 x 3 linear model for chemical production planning."""

from dataclasses import dataclass
from fractions import Fraction

from .matrix import Matrix, Reduction, rref


PRODUCTION_MATRIX: Matrix = (
    (Fraction(2), Fraction(1), Fraction(3)),
    (Fraction(1), Fraction(2), Fraction(1)),
    (Fraction(3), Fraction(1), Fraction(2)),
)
PRODUCTION_TOTALS = (Fraction(130), Fraction(80), Fraction(110))
WHAT_IF_TOTALS = (Fraction(150), Fraction(80), Fraction(110))


def augmented(matrix: Matrix, vector: tuple[Fraction, ...]) -> Matrix:
    return tuple(row + (value,) for row, value in zip(matrix, vector))


def matrix_vector_product(matrix: Matrix, vector: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(sum(value * entry for value, entry in zip(row, vector)) for row in matrix)


def matrix_product(left: Matrix, right: Matrix) -> Matrix:
    return tuple(tuple(sum(left[row][inner] * right[inner][column]
                           for inner in range(len(right)))
                       for column in range(len(right[0])))
                 for row in range(len(left)))


def determinant(matrix: Matrix) -> Fraction:
    rows = [list(row) for row in matrix]
    result = Fraction(1)
    for column in range(len(rows)):
        pivot = next((row for row in range(column, len(rows)) if rows[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            result = -result
        pivot_value = rows[column][column]
        result *= pivot_value
        for row in range(column + 1, len(rows)):
            factor = rows[row][column] / pivot_value
            for entry in range(column, len(rows)):
                rows[row][entry] -= factor * rows[column][entry]
    return result


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    identity = tuple(tuple(Fraction(int(row == column)) for column in range(size))
                     for row in range(size))
    reduced = rref(tuple(left + right for left, right in zip(matrix, identity)))
    expected = tuple(tuple(Fraction(int(row == column)) for column in range(size))
                     for row in range(size))
    if tuple(row[:size] for row in reduced.matrix) != expected:
        raise ValueError("The matrix is singular and has no inverse.")
    return tuple(row[size:] for row in reduced.matrix)


@dataclass(frozen=True)
class ProductionResult:
    matrix: Matrix
    totals: tuple[Fraction, ...]
    reduction: Reduction
    solution: tuple[Fraction, ...]
    determinant: Fraction
    inverse: Matrix
    verification: tuple[Fraction, ...]
    what_if_totals: tuple[Fraction, ...]
    what_if_solution: tuple[Fraction, ...]


def solve_totals(totals: tuple[Fraction, ...]) -> tuple[tuple[Fraction, ...], Reduction]:
    reduction = rref(augmented(PRODUCTION_MATRIX, totals))
    return tuple(row[-1] for row in reduction.matrix), reduction


def production_result() -> ProductionResult:
    solution, reduction = solve_totals(PRODUCTION_TOTALS)
    what_if_solution, _ = solve_totals(WHAT_IF_TOTALS)
    inverse_matrix = inverse(PRODUCTION_MATRIX)
    return ProductionResult(PRODUCTION_MATRIX, PRODUCTION_TOTALS, reduction, solution,
                            determinant(PRODUCTION_MATRIX), inverse_matrix,
                            matrix_vector_product(PRODUCTION_MATRIX, solution),
                            WHAT_IF_TOTALS, what_if_solution)
