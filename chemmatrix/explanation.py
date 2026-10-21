"""Compact, linear-algebra-first text for the single balancer view."""

from math import lcm

from .linear import ProductionResult, matrix_product, matrix_vector_product
from .solver import BalanceResult, format_equation, verify_atoms


def matrix_text(matrix, headers=None, labels=None) -> str:
    headers = headers or [chr(97 + i) for i in range(len(matrix[0]))]
    labels = labels or [f"R{i + 1}" for i in range(len(matrix))]
    width = max(6, *(len(str(value)) + 1 for row in matrix for value in row))
    lines = [" " * 7 + "".join(str(header).rjust(width) for header in headers)]
    lines.extend(f"{label:>6} [" + "".join(str(value).rjust(width) for value in row) + " ]"
                 for label, row in zip(labels, matrix))
    return "\n".join(lines)


def linear_expression(row) -> str:
    terms = []
    for index, value in enumerate(row):
        if value:
            term = f"{'' if abs(value) == 1 else abs(value)}{chr(97 + index)}"
            terms.append(("-" if value < 0 else ("" if not terms else "+")) + term)
    return " ".join(terms) or "0"


def system_headers(result: BalanceResult) -> list[str]:
    """Column labels for [A | b]: compounds b, c, ... (a is fixed at 1), then the constants."""
    return [chr(98 + i) for i in range(len(result.equation.compounds) - 1)] + ["rhs"]


def general_solution(reduction) -> list[str]:
    names = [chr(98 + i) for i in range(reduction.columns)]
    lines = []
    for row, pivot in enumerate(reduction.pivots):
        constant = reduction.matrix[row][-1]
        terms = [(-reduction.matrix[row][c], names[c]) for c in reduction.free_columns
                 if reduction.matrix[row][c]]
        text = str(constant) if constant or not terms else ""
        for value, name in terms:
            sign = "-" if value < 0 else "+"
            coef = abs(value)
            body = f"{'' if coef == 1 else (f'({coef})' if coef.denominator != 1 else coef)}{name}"
            text = f"{text} {sign} {body}" if text else (body if value > 0 else f"-{body}")
        lines.append(f"{names[pivot]} = {text}")
    lines.extend(f"{names[c]} = free" for c in reduction.free_columns)
    return lines


def model_text(result: BalanceResult) -> str:
    equation = result.equation
    variables = "\n".join(f"  {chr(97 + i)} = coefficient of {compound.formula}"
                          for i, compound in enumerate(equation.compounds))
    equations = "\n".join(f"  {element}: {linear_expression(row)} = 0"
                           for element, row in zip(equation.elements, result.matrix))
    n = len(equation.compounds)
    return ("CHEMICAL BALANCING MODEL\n\n"
            f"{equation.text}\n\nVARIABLES\n{variables}\n\n"
            "CONSERVATION EQUATIONS\n" + equations + "\n\n"
            "MATRIX FORM: A0 x0 = 0\n" + matrix_text(result.matrix, labels=equation.elements) + "\n\n"
            "Rows represent elements; columns represent compound coefficients.\n"
            "A balance is fixed only up to a multiple, so this homogeneous system has "
            "infinitely many solutions.\n"
            f"A0 has {len(result.matrix)} equations and {n} unknowns.\n\n"
            "NORMALIZATION: fix a = 1\n"
            "Move column a to the right-hand side: b = -(column a of A0).\n"
            "AUGMENTED MATRIX [A | b]\n"
            + matrix_text(result.normalized, headers=system_headers(result), labels=equation.elements)
            + f"\nA has {len(result.matrix)} equations and {n - 1} unknowns.")


def solution_text(result: BalanceResult) -> str:
    reduction = result.reduction
    lines = ["BALANCE FROM RREF", f"Rank = {reduction.rank}",
             f"Free variables = {len(reduction.free_columns)}"]
    if result.solution:
        lines.append("Solution with a = 1: (" + ", ".join(map(str, result.solution)) + ")^T")
        scale = lcm(*(value.denominator for value in result.solution))
        if scale != 1:
            lines.append(f"Multiply by {scale} to clear fractions.")
    elif reduction.consistent:
        lines.append("General solution with a = 1:")
        lines.extend("  " + line for line in general_solution(reduction))
    lines.extend([result.message, format_equation(result.equation, result.coefficients)
                  if result.coefficients else "No positive balance selected."])
    return "\n".join(lines)


def verification_text(result: BalanceResult) -> str:
    if not result.coefficients:
        return "CHEMICAL VERIFICATION\n\n" + result.message
    counts = verify_atoms(result.equation, result.coefficients)
    residual = tuple(sum(a * b for a, b in zip(row, result.coefficients)) for row in result.matrix)
    rows = "\n".join(f"{count.element}: {count.reactants} = {count.products}"
                      for count in counts)
    A = tuple(row[:-1] for row in result.normalized)
    b = tuple(row[-1] for row in result.normalized)
    product = matrix_vector_product(A, result.solution[1:])
    return ("CHEMICAL VERIFICATION\n\n" + format_equation(result.equation, result.coefficients)
            + "\n\n" + rows + "\n\n"
            + "A x = (" + ", ".join(map(str, product)) + ")^T = (" + ", ".join(map(str, b)) + ")^T = b\n"
            + "A0 x0 = (" + ", ".join(map(str, residual)) + ")^T = 0")


def production_text(result: ProductionResult) -> str:
    identity = matrix_product(result.matrix, result.inverse)
    identity_text = matrix_text(identity, headers=("", "", ""), labels=("", "", ""))
    return ("LINEAR ALGEBRA EXTENSION: CHEMICAL PRODUCTION\n\n"
            "A chemical plant makes three product batches using three limited resources.\n"
            "x1 = small batches, x2 = standard batches, x3 = large batches.\n\n"
            "2x1 + x2 + 3x3 = 130\n"
            "x1 + 2x2 + x3 = 80\n"
            "3x1 + x2 + 2x3 = 110\n\n"
            "A x = b, with A =\n"
            + matrix_text(result.matrix, headers=("x1", "x2", "x3"),
                          labels=("R1", "R2", "R3"))
            + "\nb = (130, 80, 110)^T\n\n"
            "GAUSS-JORDAN ON [A | b]\n"
            + matrix_text(result.reduction.matrix, headers=("x1", "x2", "x3", "b"))
            + "\nSolution: x = (" + ", ".join(map(str, result.solution)) + ")^T\n"
            f"det(A) = {result.determinant}, so A is invertible and this solution is unique.\n\n"
            "MATRIX VERIFICATION\n"
            "Ax = (" + ", ".join(map(str, result.verification)) + ")^T = b\n"
            "A A^-1 = I\n" + identity_text + "\n\n"
            "INTERPRETATION AND METHOD COMPARISON\n"
            "The solution gives the batch quantities required by the three resource totals. "
            "Gauss-Jordan is used because every elementary row operation is visible and "
            "it works directly on [A | b]. The inverse method is useful when A stays fixed "
            "for repeated supply changes. Cramer's rule is valid here because det(A) != 0, "
            "but three replacement determinants are less efficient for larger systems.\n\n"
            "WHAT-IF: CHANGE b\n"
            "Change b to (150, 80, 110)^T and reuse A^-1:\n"
            "x_new = A^-1 b_new = (" + ", ".join(map(str, result.what_if_solution)) + ")^T\n"
            "The changed resource total produces a different, fractional batch plan.")


def worked_solution(result: BalanceResult, production: ProductionResult | None = None) -> str:
    steps = "\n\n".join(
        f"STEP {index}: {step.description}\n{matrix_text(step.matrix, headers=system_headers(result))}"
        for index, step in enumerate(result.reduction.steps, start=1))
    text = (model_text(result) + "\n\nROW OPERATIONS\n" + steps + "\n\n"
            + solution_text(result) + "\n\n" + verification_text(result))
    if production:
        text += "\n\n" + production_text(production)
    return text