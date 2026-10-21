"""Core checks for the chemical balancer."""

from fractions import Fraction as F
import unittest

from chemmatrix.explanation import model_text, worked_solution
from chemmatrix.matrix import rref
from chemmatrix.parser import EquationError, parse_equation, parse_formula
from chemmatrix.solver import balance, verify_atoms


class ParserTests(unittest.TestCase):
    def test_formula_and_equation(self):
        self.assertEqual(parse_formula("Al2(SO4)3"), {"Al": 2, "S": 3, "O": 12})
        self.assertEqual(parse_equation("H2 + O2 -> H2O").text, "H2 + O2 -> H2O")
        with self.assertRaises(EquationError):
            parse_formula("CuSO4·5H2O")


class BalancerTests(unittest.TestCase):
    def test_reference_balances_and_verification(self):
        result = balance("C3H8 + O2 -> CO2 + H2O")
        self.assertEqual(result.coefficients, (1, 5, 3, 4))
        self.assertTrue(all(count.matches for count in verify_atoms(result.equation, result.coefficients)))
        self.assertIn("MATRIX FORM: A0 x0 = 0", model_text(result))
        self.assertIn("ROW OPERATIONS", worked_solution(result))

    def test_row_operations_replay(self):
        original = [[0, 2, 3], [2, 1, -1], [4, 2, -2]]
        reduction = rref(original)
        rows = [list(map(F, row)) for row in original]
        for step in reduction.steps[1:]:
            if step.kind == "swap":
                rows[step.target], rows[step.source] = rows[step.source], rows[step.target]
            elif step.kind == "scale":
                rows[step.target] = [value * step.factor for value in rows[step.target]]
            else:
                rows[step.target] = [a + step.factor * b for a, b in zip(rows[step.target], rows[step.source])]
            self.assertEqual(tuple(map(tuple, rows)), step.matrix)


if __name__ == "__main__":
    unittest.main()
