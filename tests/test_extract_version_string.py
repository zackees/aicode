"""
Unit test file.
"""

import unittest

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


if __name__ == "__main__":
    unittest.main()
