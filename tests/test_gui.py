"""Tk checks for the single-page balancer."""

import tkinter as tk
import unittest

from chemmatrix.gui import ChemMatrixApp, COMMON_EQUATIONS


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
        except tk.TclError as error:
            raise unittest.SkipTest(f"Graphical Tk session unavailable: {error}")
        cls.callback_errors = []
        cls.root.report_callback_exception = lambda *args: cls.callback_errors.append(args)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def tearDown(self):
        self.assertEqual(self.callback_errors, [])

    def test_single_balancer_surface_and_inline_solution(self):
        app = ChemMatrixApp(self.root)
        self.root.update()
        text = app.solution_view.text.get("1.0", "end-1c")
        self.assertEqual(len(COMMON_EQUATIONS), 11)
        self.assertEqual(app.result.coefficients, (1, 5, 3, 4))
        self.assertIn("ROW OPERATIONS", text)
        self.assertIn("A x =", text)
        app.destroy()

    def test_common_equation_and_copy(self):
        app = ChemMatrixApp(self.root)
        app.common_choice.current(1)
        app.common_choice.event_generate("<<ComboboxSelected>>")
        self.root.update()
        self.assertEqual(app.result.coefficients, (4, 3, 2))
        app.copy_solution()
        copied = self.root.clipboard_get()
        self.assertIn("CHEMICAL BALANCING MODEL", copied)
        app.destroy()


if __name__ == "__main__":
    unittest.main()
