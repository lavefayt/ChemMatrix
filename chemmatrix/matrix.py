"""Exact Gauss–Jordan elimination, including replayable elementary operations."""

from dataclasses import dataclass
from fractions import Fraction


Matrix = tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class RowStep:
    kind: str
    target: int
    source: int | None
    factor: Fraction
    matrix: Matrix

    @property
    def description(self) -> str:
        target = f"R{self.target + 1}"
        if self.kind == "initial":
            return "Initial augmented matrix [A | b]"
        if self.kind == "swap":
            return f"{target} <-> R{self.source + 1}"
        if self.kind == "scale":
            return f"{target} <- ({self.factor}) {target}"
        return f"{target} <- {target} + ({self.factor}) R{self.source + 1}"


@dataclass(frozen=True)
class Reduction:
    matrix: Matrix
    pivots: tuple[int, ...]
    steps: tuple[RowStep, ...]
    columns: int  # coefficient columns; any columns after these are right-hand sides

    @property
    def rank(self) -> int:
        return len(self.pivots)

    @property
    def free_columns(self) -> tuple[int, ...]:
        return tuple(c for c in range(self.columns) if c not in self.pivots)

    @property
    def consistent(self) -> bool:
        """False when a row of zeros in A has a nonzero right-hand side."""
        return not any(any(row[self.columns:]) for row in self.matrix[self.rank:])


def rref(values, pivot_columns: int | None = None) -> Reduction:
    """Reduce a nonempty rectangular matrix, preserving a snapshot per operation.

    Three passes, in the order used on the slides:
      1. Forward: swap a nonzero entry into each pivot position, clear entries below it.
      2. Scale: make every pivot a leading 1, top row to bottom row.
      3. Backward: clear entries above each pivot, left column to right column.
    Only the first `pivot_columns` columns may hold pivots (the rest is the right-hand side).
    """
    rows = [list(map(Fraction, row)) for row in values]
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("A matrix must be nonempty and rectangular.")
    width = len(rows[0])
    columns = width if pivot_columns is None else pivot_columns
    if not 1 <= columns <= width:
        raise ValueError("pivot_columns must be between 1 and the number of columns.")

    def snapshot() -> Matrix:
        return tuple(tuple(row) for row in rows)

    steps = [RowStep("initial", 0, None, Fraction(1), snapshot())]
    pivots: list[int] = []

    # Pass 1: forward elimination (row-echelon structure).
    target = 0
    for column in range(columns):
        if target == len(rows):
            break
        source = next((r for r in range(target, len(rows)) if rows[r][column]), None)
        if source is None:
            continue
        if source != target:
            rows[target], rows[source] = rows[source], rows[target]
            steps.append(RowStep("swap", target, source, Fraction(1), snapshot()))
        for row in range(target + 1, len(rows)):
            if rows[row][column]:
                factor = -rows[row][column] / rows[target][column]
                rows[row] = [a + factor * b for a, b in zip(rows[row], rows[target])]
                steps.append(RowStep("add", row, target, factor, snapshot()))
        pivots.append(column)
        target += 1

    # Pass 2: leading 1 in every pivot row.
    for row, column in enumerate(pivots):
        if rows[row][column] != 1:
            factor = 1 / rows[row][column]
            rows[row] = [value * factor for value in rows[row]]
            steps.append(RowStep("scale", row, None, factor, snapshot()))

    # Pass 3: clear above each pivot.
    for row, column in enumerate(pivots):
        for above in range(row):
            if rows[above][column]:
                factor = -rows[above][column]
                rows[above] = [a + factor * b for a, b in zip(rows[above], rows[row])]
                steps.append(RowStep("add", above, row, factor, snapshot()))

    return Reduction(snapshot(), tuple(pivots), tuple(steps), columns)