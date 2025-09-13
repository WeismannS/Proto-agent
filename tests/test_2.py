import unittest
import sys
import os


class TestCalculatorFunctionality(unittest.TestCase):
    def test_calculator_functioanlity(self):
        sys.path.insert(
            0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "calculator")
        )
        try:
            from pkg.calculator import Calculator  # type: ignore

            calc = Calculator()
            result = calc.evaluate("3 + 5")
            self.assertEqual(result, 8)
        finally:
            sys.path.pop(0)
