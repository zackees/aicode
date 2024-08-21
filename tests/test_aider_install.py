"""
Unit test file.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from aicode.aider_control import aider_install, aider_run


class ExtractVersionStringTester(unittest.TestCase):
    """Main tester class."""

    def test_install(self) -> None:
        """Tests we can extract strings like '0.40.7-dev'."""
        with TemporaryDirectory() as temp_dir:
            aider_install(Path(temp_dir))
            aider_run(["aider", "--help"])


if __name__ == "__main__":
    unittest.main()
