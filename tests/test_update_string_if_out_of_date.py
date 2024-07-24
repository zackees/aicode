"""
Unit test file.
"""

import unittest

from aicode.util import aider_fetch_update_string_if_out_of_date


class FetchUpdateStringIfOutOfDateTester(unittest.TestCase):
    """Main tester class."""

    def test_weird_version(self) -> None:
        """Tests we can extract strings like '0.40.7-dev'."""
        new_version = aider_fetch_update_string_if_out_of_date()
        if new_version:
            self.assertTrue(isinstance(new_version, str))
            print("New version available: ", new_version)
        # if parsing is unsuccessful an exception is thrown


if __name__ == "__main__":
    unittest.main()
