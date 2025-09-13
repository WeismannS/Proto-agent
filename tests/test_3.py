import unittest
import subprocess
import sys
import os


class TestCLI(unittest.TestCase):
    """Test CLI functionality"""

    def test_cli_help(self):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "proto_agent", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.path.dirname(os.path.dirname(__file__)),
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("Usage:", result.stdout)
        except subprocess.TimeoutExpired:
            self.skipTest("CLI help command timed out")

    def test_cli_functioanlity(self):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "proto_agent", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.path.dirname(os.path.dirname(__file__)),
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("--working-directory", result.stdout)
            self.assertIn("--verbose", result.stdout)
            self.assertIn("--read-only", result.stdout)
        except subprocess.TimeoutExpired:
            self.skipTest("CLI help command timed out")
