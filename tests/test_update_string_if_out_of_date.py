"""
Unit test file.
"""

import unittest

from aicode.aider_control import AiderUpdateResult, aider_fetch_update_status
from aicode.main import aider_install_if_missing


class FetchUpdateStringIfOutOfDateTester(unittest.TestCase):
    """Main tester class."""

    def test_weird_version(self) -> None:
        """Tests we can extract strings like '0.40.7-dev'."""
        aider_install_if_missing()
        update_status = aider_fetch_update_status()
        self.assertIsInstance(update_status, AiderUpdateResult)
        self.assertIsInstance(update_status.latest_version, str)
        self.assertIsInstance(update_status.current_version, str)
        self.assertIsInstance(update_status.has_update, bool)
        self.assertNotEqual(update_status.latest_version, "Unknown")
        self.assertNotEqual(update_status.current_version, "Unknown")
        if update_status.latest_version != update_status.current_version:
            self.assertTrue(update_status.has_update)


if __name__ == "__main__":
    unittest.main()
