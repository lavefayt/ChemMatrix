"""Plain-text teaching views shared by the interface and clipboard export."""

from math import gcd, lcm
from functools import reduce

from .solver import BalanceResult, format_equation, verify_atoms


def matrix_text(matrix, headers=None, labels=None) -> str:
    headers = headers or [chr(97 + i) for i in range(len(matrix[0]))]
    labels = labels or [f"R{i + 1}" for i in range(len(matrix))]
    width = max(5, *(len(str(value)) + 1 for row in matrix for value in row))
    label_width = max(4, *(len(label) for label in labels))
    lines = [" " * (label_width + 3) + "".join(str(h).rjust(width) for h in headers)]
    for label, row in zip(labels, matrix):
        lines.append(f"{label:>{label_width}} [ " + "".join(str(v).rjust(width) for v in row) + " ]")
    return "\n".join(lines)


def linear_expression(row) -> str:
    terms = []
    for i, value in enumerate(row):
        if not value:
            continue
        magnitude = abs(value)
        term = f"{'' if magnitude == 1 else magnitude}{chr(97 + i)}"
        if not terms:
            terms.append(("-" if value < 0 else "") + term)
        else:
            terms.append((" - " if value < 0 else " + ") + term)
    return "".join(terms) or "0"


def model_text(result: BalanceResult) -> str:
    equation = result.equation
    variables = "\n".join(f"  {chr(97 + i)} = coefficient of {c.formula}"
                          for i, c in enumerate(equation.compounds))
    equations = "\n".join(f"  {element}: {linear_expression(row)} = 0"
                          for element, row in zip(equation.elements, result.matrix))
    rows, columns = len(result.matrix), len(equation.compounds)
    determinant = ("A is rectangular, so its determinant is not defined."
                   if rows != columns else
                   ("A is square with full rank: det(A) is nonzero, so only x = 0 solves Ax = 0."
                    if result.reduction.rank == columns else
                    "A is square and singular: det(A) = 0, so a nontrivial nullspace exists."))
    return (f"EQUATION\n{equation.text}\n\nUNKNOWNS\n{variables}\n\n"
            f"CONSERVATION EQUATIONS\n{equations}\n\nMATRIX FORM: A x = 0\n"
            f"x = ({', '.join(chr(97 + i) for i in range(columns))})^T\n\n"
            f"{matrix_text(result.matrix, labels=equation.elements)}\n\n"
            "Rows = elements; columns = compound coefficients.\n"
            "Reactant atom counts are positive; product counts are negative.\n"
            "The right-hand vector contains one zero per element.\n\n"
            f"A has {rows} rows and {columns} columns.\n{determinant}\n"
            "A nontrivial nullspace alone does not guarantee strictly positive coefficients.")


def solution_text(result: BalanceResult) -> str:
    reduction = result.reduction
    names = lambda columns: ", ".join(chr(97 + i) for i in columns) or "none"
    lines = [f"Rank = {reduction.rank}", f"Pivot variables: {names(reduction.pivots)}",
             f"Free variables: {names(reduction.free_columns)}",
             f"Nullity = {len(result.equation.compounds)} - {reduction.rank} = {len(reduction.basis)}", ""]
    if not reduction.basis:
        lines.append("General solution: x = 0.")
    else:
        terms = [f"t{i + 1} * ({', '.join(map(str, vector))})"
                 for i, vector in enumerate(reduction.basis)]
        lines.append("General solution: x = " + " + ".join(terms))
        lines.append("Parameters t1, t2, ... are arbitrary real numbers.")
        if len(reduction.basis) == 1:
            vector = reduction.basis[0]
            if all(value < 0 for value in vector):
                vector = tuple(-value for value in vector)
                lines.append("Reverse the basis vector's sign to make every entry positive.")
            if result.coefficients:
                denominator = lcm(*(value.denominator for value in vector))
                integers = tuple(int(value * denominator) for value in vector)
                divisor = reduce(gcd, integers)
                lines.extend([f"Set t1 = 1: x = ({', '.join(map(str, vector))})",
                              f"LCM of denominators = {denominator}",
                              f"Multiply by {denominator}: ({', '.join(map(str, integers))})",
                              f"GCD of these integers = {divisor}",
                              f"Divide by {divisor}: {result.coefficients}",
                              "All positive integer multiples also balance; this is the smallest ratio."])
    lines.extend(["", result.message])
    if result.coefficients:
        lines.extend(["", format_equation(result.equation, result.coefficients)])
    return "\n".join(lines)


def counts_text(counts) -> str:
    lines = [f"{'Element':<10}{'Reactants':>12}{'Products':>12}  Match"]
    lines.extend(f"{c.element:<10}{c.reactants:>12}{c.products:>12}  {'Yes' if c.matches else 'No'}"
                 for c in counts)
    return "\n".join(lines)


def verification_text(result: BalanceResult) -> str:
    if not result.coefficients:
        return "No positive coefficient vector was selected.\n\n" + result.message
    counts = verify_atoms(result.equation, result.coefficients)
    residual = tuple(sum(a * b for a, b in zip(row, result.coefficients)) for row in result.matrix)
    return (format_equation(result.equation, result.coefficients) + "\n\n" + counts_text(counts)
            + "\n\nA x = (" + ", ".join(map(str, residual)) + ")^T = 0\n"
            "Every element has the same atom total on both sides.\n\n"
            "Coefficients give relative amounts of molecules or moles.\n"
            "Atom balance alone does not establish whether a reaction occurs.")


def worked_solution(result: BalanceResult) -> str:
    steps = "\n\n".join(f"Step {i}: {step.description}\n{matrix_text(step.matrix)}"
                          for i, step in enumerate(result.reduction.steps))
    return ("CHEMMATRIX WORKED SOLUTION\n\n" + model_text(result) + "\n\nROW REDUCTION\n"
            + steps + "\n\nSOLUTION\n" + solution_text(result)
            + "\n\nVERIFICATION\n" + verification_text(result))
