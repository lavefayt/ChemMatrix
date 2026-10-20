"""Exercise real Tk widgets; skipped when a graphical Tk session is unavailable."""

import tkinter as tk
import unittest

from chemmatrix.gui import ChemMatrixApp


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

    def setUp(self):
        self.app = ChemMatrixApp(self.root)
        self.root.update()

    def tearDown(self):
        self.app.destroy()
        self.assertEqual(self.callback_errors, [])

    def text(self, view):
        return view.text.get("1.0", "end-1c")

    def fill(self, values):
        for variable, value in zip(self.app.practice_vars, values):
            variable.set(value)

    def test_balance_navigation_clipboard_and_invalidation(self):
        app = self.app
        app.balance_button.invoke()
        self.assertEqual(app.result.coefficients, (1, 5, 3, 4))
        self.assertIn("3a - c = 0", self.text(app.model_view))
        app.views.select(app.steps_page)
        self.root.update()
        while app.next_button.instate(["!disabled"]):
            app.next_button.invoke()
        self.assertIn("LCM of denominators = 4", self.text(app.steps_view))
        self.assertTrue(app.next_button.instate(["disabled"]))
        app.previous_button.invoke()
        self.assertTrue(app.next_button.instate(["!disabled"]))
        app.copy_button.invoke()
        self.assertIn("C3H8 + 5O2 -> 3CO2 + 4H2O", self.root.clipboard_get())
        self.assertIn("A x = (0, 0, 0)^T = 0", self.text(app.verify_view))
        app.input_var.set("Fe + O2 -> Fe2O3")
        self.assertIsNone(app.result)
        self.assertEqual(self.text(app.verify_view), "")
        self.assertTrue(app.copy_button.instate(["disabled"]))
        app.balance_button.invoke()
        self.assertEqual(app.result.coefficients, (4, 3, 2))
        app.clear_button.invoke()
        self.assertEqual(app.input_var.get(), "")

    def test_errors_and_exceptional_systems(self):
        app = self.app
        for equation, message in [("H2O(l) -> H2 + O2", "physical-state"),
                                   ("2H2 + O2 -> H2O", "leading coefficients")]:
            app.input_var.set(equation)
            app.balance_button.invoke()
            self.assertIn(message, app.status_var.get())
            self.assertIsNone(app.result)
        for equation in ("H2 -> O2", "H2 + O2 -> H2", "C + O2 -> CO + CO2"):
            app.load_example(equation)
            self.assertIsNotNone(app.result)
            self.assertIsNone(app.result.coefficients)
            self.assertIn("No positive coefficient vector", self.text(app.verify_view))
            app.copy_button.invoke()

    def test_practice_feedback_and_progress(self):
        app = self.app
        app.tabs.select(app.practice)
        self.root.update()
        app.check_button.invoke()
        self.assertIn("positive integer", self.text(app.practice_view))
        self.fill(["1", "1", "1"])
        app.check_button.invoke()
        self.assertIn("Check these elements: O", self.text(app.practice_view))
        self.fill(["4", "2", "4"])
        app.check_button.invoke()
        self.assertIn("common factor", self.text(app.practice_view))
        self.assertEqual(len(app.solved), 0)
        self.fill(["2", "1", "2"])
        app.check_button.invoke()
        self.assertEqual(app.solved, {0})
        app.practice_vars[0].set("3")
        self.assertIn("Answer changed", self.text(app.practice_view))
        app.retry_button.invoke()
        self.assertEqual([v.get() for v in app.practice_vars], ["", "", ""])
        app.exercise_choice.current(5)
        app.exercise_choice.event_generate("<<ComboboxSelected>>")
        self.root.update()
        self.assertEqual(len(app.practice_entries), 4)
        app.hint_button.invoke()
        self.assertIn("carbon", self.text(app.practice_view))
        app.reveal_button.invoke()
        self.assertIn("ROW REDUCTION", self.text(app.practice_view))
        self.fill(["1", "5", "3", "4"])
        app.check_button.invoke()
        self.assertEqual(app.solved, {0})
        self.assertEqual(app.assisted, {5})
        app.exercise_choice.current(0)
        app.load_exercise()
        self.assertIn("1 / 10", app.progress_var.get())

    def test_resize_scroll_and_keyboard(self):
        app = self.app
        self.root.geometry("800x650")
        self.root.update()
        app.equation_entry.focus_force()
        self.root.update()
        app.equation_entry.event_generate("<Return>")
        self.root.update()
        self.assertIsNotNone(app.result)
        app.equation_entry.event_generate("<Tab>")
        self.root.update()
        self.assertEqual(self.root.focus_get(), app.balance_button)
        app.reveal_practice()
        app.tabs.select(app.practice)
        self.root.update()
        app.practice_view.text.yview_moveto(1)
        self.root.update()
        self.assertGreater(app.practice_view.text.yview()[0], 0)
        self.assertLessEqual(app.practice_view.winfo_rooty() + app.practice_view.winfo_height(),
                             self.root.winfo_rooty() + self.root.winfo_height())
        self.root.geometry("1280x900")
        self.root.update()
        self.assertGreater(app.practice_view.winfo_height(), 300)

    def test_restart_resets_session(self):
        self.app.solved.add(0)
        self.app.assisted.add(1)
        self.app.destroy()
        self.app = ChemMatrixApp(self.root)
        self.assertEqual(self.app.solved, set())
        self.assertEqual(self.app.assisted, set())


if __name__ == "__main__":
    unittest.main()
