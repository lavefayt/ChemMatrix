"""Core checks for the chemical balancer and its linear algebra extension."""

from fractions import Fraction as F
import unittest

from chemmatrix.explanation import model_text, production_text, worked_solution
from chemmatrix.linear import (PRODUCTION_MATRIX, PRODUCTION_TOTALS, determinant,
                               matrix_product, matrix_vector_product, production_result)
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
        self.assertIn("MATRIX FORM: A x = 0", model_text(result))
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


class ExtensionTests(unittest.TestCase):
    def test_unique_three_by_three_solution(self):
        result = production_result()
        self.assertEqual(result.solution, (F(10), F(20), F(30)))
        self.assertEqual(result.determinant, F(-8))
        self.assertEqual(result.verification, PRODUCTION_TOTALS)
        self.assertIn("det(A) = -8", production_text(result))

    def test_inverse_and_what_if(self):
        result = production_result()
        identity = matrix_product(result.matrix, result.inverse)
        expected = tuple(tuple(F(int(row == column)) for column in range(3)) for row in range(3))
        self.assertEqual(identity, expected)
        self.assertEqual(matrix_vector_product(PRODUCTION_MATRIX, result.solution), PRODUCTION_TOTALS)
        self.assertEqual(result.what_if_solution, (F(5, 2), F(35, 2), F(85, 2)))


if __name__ == "__main__":
    unittest.main()
