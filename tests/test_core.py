"""Core acceptance checks: run python -m unittest tests.test_core -v."""

from fractions import Fraction as F
from math import gcd
from functools import reduce
import unittest

from chemmatrix.explanation import model_text, worked_solution
from chemmatrix.matrix import rref
from chemmatrix.parser import EquationError, parse_equation, parse_formula
from chemmatrix.practice import EXERCISES, check_answer
from chemmatrix.solver import balance, normalize_coefficients, verify_atoms


class ParserTests(unittest.TestCase):
    def test_counts_repeated_and_nested(self):
        self.assertEqual(parse_formula("CH3COOH"), {"C": 2, "H": 4, "O": 2})
        self.assertEqual(parse_formula("Al2(SO4)3"), {"Al": 2, "S": 3, "O": 12})
        self.assertEqual(parse_formula("Ca((OH)2)2"), {"Ca": 1, "O": 4, "H": 4})

    def test_separators(self):
        for separator in ("->", "→", "="):
            self.assertEqual(parse_equation(f" H2 + O2 {separator} H2O ").text, "H2 + O2 -> H2O")

    def test_invalid_formulas(self):
        for formula in ("", "Xx2", "h2", "2H2O", "H0", "H01", "H1000", "H2O(l)",
                        "CuSO4·5H2O", "Na+", "SO4^2-", "()", "(H2", "H2)", "H 2", "H₂", "[OH]2"):
            with self.subTest(formula=formula), self.assertRaises(EquationError):
                parse_formula(formula)

    def test_empty_sides_and_terms(self):
        for equation in ("", "H2", "-> H2", "H2 ->", "H2 + -> H2O", "H2 -> H2 -> H2", "Na+ + Cl -> NaCl"):
            with self.subTest(equation=equation), self.assertRaises(EquationError):
                parse_equation(equation)

    def test_limits(self):
        self.assertEqual(parse_formula("((((H)2)2)2)2"), {"H": 16})
        self.assertEqual(parse_formula("H999"), {"H": 999})
        for equation in ("H" * 501 + " -> H", "(((((H))))) -> H", "+".join(["H"] * 12) + " -> H",
                         "HHeLiBeBCNOFNeNaMgAl -> H"):
            with self.subTest(equation=equation), self.assertRaises(EquationError):
                parse_equation(equation)
        self.assertEqual(len(parse_equation("+".join(["H"] * 11) + " -> H").compounds), 12)
        self.assertEqual(len(parse_equation("HHeLiBeBCNOFNeNaMg -> H").elements), 12)
        # Exactly 500 input characters, including whitespace, is allowed.
        self.assertEqual(parse_equation("H -> H" + " " * 494).text, "H -> H")


class MatrixTests(unittest.TestCase):
    def test_operations_replay(self):
        original = [[0, 2, 3], [2, 1, -1], [4, 2, -2]]
        reduced = rref(original)
        rows = [list(map(F, row)) for row in original]
        self.assertEqual(reduced.steps[0].kind, "initial")
        kinds = set()
        for step in reduced.steps[1:]:
            kinds.add(step.kind)
            if step.kind == "swap":
                rows[step.target], rows[step.source] = rows[step.source], rows[step.target]
            elif step.kind == "scale":
                rows[step.target] = [v * step.factor for v in rows[step.target]]
            else:
                rows[step.target] = [a + step.factor * b for a, b in zip(rows[step.target], rows[step.source])]
            self.assertEqual(tuple(map(tuple, rows)), step.matrix)
        self.assertEqual(kinds, {"swap", "scale", "add"})
        self.assertEqual(reduced.rank, 2)
        self.assertEqual(reduced.free_columns, (2,))
        self.assertEqual(reduced.basis, ((F(5, 4), F(-3, 2), F(1)),))
        self.assertEqual(original, [[0, 2, 3], [2, 1, -1], [4, 2, -2]])

    def test_zero_and_full_rank(self):
        self.assertEqual(len(rref([[0, 0], [0, 0]]).basis), 2)
        self.assertEqual(rref([[1, 0], [0, 1]]).basis, ())
        for values in ([], [[]], [[1], [1, 2]]):
            with self.assertRaises(ValueError):
                rref(values)


class SolverTests(unittest.TestCase):
    def test_reference_balances(self):
        for equation, expected in [("C3H8 + O2 -> CO2 + H2O", (1, 5, 3, 4)),
                                   ("Fe + O2 -> Fe2O3", (4, 3, 2)),
                                   ("Ca(OH)2 + HCl -> CaCl2 + H2O", (1, 2, 1, 2))]:
            with self.subTest(equation=equation):
                result = balance(equation)
                self.assertEqual(result.status, "balanced")
                self.assertEqual(result.coefficients, expected)
                self.assertTrue(all(c.matches for c in verify_atoms(result.equation, expected)))
                self.assertTrue(all(sum(a * b for a, b in zip(row, expected)) == 0 for row in result.matrix))

    def test_exceptional_systems(self):
        for equation, status in [("H2 -> O2", "zero_only"), ("H2 + O2 -> H2", "no_positive"),
                                  ("H2 + H2O -> O2", "no_positive"),
                                  ("C + O2 -> CO + CO2", "multiple_free")]:
            with self.subTest(equation=equation):
                result = balance(equation)
                self.assertEqual(result.status, status)
                self.assertIsNone(result.coefficients)
                for vector in result.reduction.basis:
                    self.assertTrue(all(sum(a * b for a, b in zip(row, vector)) == 0 for row in result.matrix))

    def test_normalization(self):
        self.assertEqual(normalize_coefficients([F(1, 3), F(2, 3)]), (1, 2))
        self.assertEqual(normalize_coefficients([-4, -8]), (1, 2))
        for values in ([], [0, 1], [-1, 1]):
            with self.assertRaises(ValueError):
                normalize_coefficients(values)

    def test_verification_validation(self):
        eq = parse_equation("H2 + O2 -> H2O")
        self.assertFalse(all(c.matches for c in verify_atoms(eq, [1, 1, 1])))
        for coefficients in ([1], [0, 1, 1], [-1, 1, 1], [True, 1, 1], [1.0, 1, 1]):
            with self.assertRaises(ValueError):
                verify_atoms(eq, coefficients)

    def test_teaching_output(self):
        result = balance("C3H8 + O2 -> CO2 + H2O")
        text = worked_solution(result)
        self.assertIn("3a - c = 0", text)
        self.assertIn("8a - 2d = 0", text)
        self.assertIn("2b - 2c - d = 0", text)
        self.assertIn("(1/4, 5/4, 3/4, 1)", text)
        self.assertIn("LCM of denominators = 4", text)
        self.assertIn("C3H8 + 5O2 -> 3CO2 + 4H2O", text)
        self.assertIn("determinant is not defined", text)
        self.assertIn("det(A) = 0", model_text(balance("H2O -> H2O")))
        self.assertIn("det(A) is nonzero", model_text(balance("H2 -> O2")))


class PracticeTests(unittest.TestCase):
    def test_curated_exercises(self):
        self.assertEqual(len(EXERCISES), 10)
        for exercise in EXERCISES:
            with self.subTest(exercise=exercise.title):
                result = balance(exercise.equation)
                self.assertEqual(result.status, "balanced")
                self.assertEqual(reduce(gcd, result.coefficients), 1)
                self.assertEqual(check_answer(exercise, result.coefficients).status, "correct")

    def test_feedback(self):
        exercise = EXERCISES[0]
        self.assertEqual(check_answer(exercise, ["2", "1", "2"]).status, "correct")
        self.assertEqual(check_answer(exercise, ["4", "2", "4"]).status, "proportional")
        wrong = check_answer(exercise, ["1", "1", "1"])
        self.assertEqual(wrong.status, "incorrect")
        self.assertIn("O", wrong.message)
        for entries in (["", "1", "1"], ["-1", "1", "1"], ["0", "1", "1"],
                        ["1.5", "1", "1"], ["1"], ["1000000", "1", "1"], ["²", "1", "1"]):
            self.assertEqual(check_answer(exercise, entries).status, "invalid")


if __name__ == "__main__":
    unittest.main()
