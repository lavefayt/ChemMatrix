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
            return "Initial conservation matrix A (right-hand side is zero)"
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

    @property
    def rank(self) -> int:
        return len(self.pivots)

    @property
    def free_columns(self) -> tuple[int, ...]:
        return tuple(c for c in range(len(self.matrix[0])) if c not in self.pivots)

    @property
    def basis(self) -> Matrix:
        vectors = []
        for free in self.free_columns:
            vector = [Fraction(0)] * len(self.matrix[0])
            vector[free] = Fraction(1)
            for row, pivot in enumerate(self.pivots):
                vector[pivot] = -self.matrix[row][free]
            vectors.append(tuple(vector))
        return tuple(vectors)


def rref(values) -> Reduction:
    """Reduce a nonempty rectangular matrix, preserving a snapshot per operation."""
    rows = [list(map(Fraction, row)) for row in values]
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("A matrix must be nonempty and rectangular.")

    def snapshot() -> Matrix:
        return tuple(tuple(row) for row in rows)

    steps = [RowStep("initial", 0, None, Fraction(1), snapshot())]
    pivots = []
    target = 0
    for column in range(len(rows[0])):
        source = next((r for r in range(target, len(rows)) if rows[r][column]), None)
        if source is None:
            continue
        if source != target:
            rows[target], rows[source] = rows[source], rows[target]
            steps.append(RowStep("swap", target, source, Fraction(1), snapshot()))
        if rows[target][column] != 1:
            factor = 1 / rows[target][column]
            rows[target] = [value * factor for value in rows[target]]
            steps.append(RowStep("scale", target, None, factor, snapshot()))
        for row in range(len(rows)):
            if row != target and rows[row][column]:
                factor = -rows[row][column]
                rows[row] = [a + factor * b for a, b in zip(rows[row], rows[target])]
                steps.append(RowStep("add", row, target, factor, snapshot()))
        pivots.append(column)
        target += 1
        if target == len(rows):
            break
    return Reduction(snapshot(), tuple(pivots), tuple(steps))
