"""
Unit test file.
"""

import unittest

from aicode.main import extract_version_string


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


if __name__ == "__main__":
    unittest.main()
