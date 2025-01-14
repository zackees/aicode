"""
Unit test file.
"""

import unittest

from aicode.aider_update_result import Version
from aicode.util import extract_version_string


class ExtractVersionStringTester(unittest.TestCase):
    """Main tester class."""

    def test_weird_version(self) -> None:
        """Tests we can extract strings like '0.40.7-dev'."""
        version = extract_version_string("0.40.7-dev")
        self.assertEqual("0.40.7-dev", version)

    def test_normal_version(self) -> None:
        """Tests we can extract strings like '0.40.7'."""
        version = extract_version_string("0.40.7")
        self.assertEqual("0.40.7", version)

    def test_bug(self) -> None:
        test_str = "aider 0.45.1"
        version = extract_version_string(test_str)
        self.assertEqual("0.45.1", version)

    def test_version_comparators(self) -> None:
        a = Version("0.40.7")
        b = Version("0.40.6")
        self.assertTrue(a > b)
        self.assertFalse(a < b)
        self.assertFalse(a == b)
        self.assertTrue(a >= b)
        self.assertFalse(a <= b)
        self.assertEqual(str(a), "0.40.7")


if __name__ == "__main__":
    unittest.main()
