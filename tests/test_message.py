"""
Unit test for message file functionality.
"""

import os
import subprocess
import tempfile
import unittest


class MessageFileTester(unittest.TestCase):
    """Test class for message file functionality."""

    @unittest.skip(
        "This will block forever, we need an option for a file to run this in script mode."
    )
    def test_message_file_arg(self) -> None:
        """Test that --message-file argument is properly passed to aider."""
        # Create a temporary message file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Test message for aider")
            temp_path = temp_file.name

        stdout: str = "NOTHING YET"
        stderr: str = "NOTHING YET"

        try:
            # Run aicode with --message-file and capture the command that would be executed
            result = subprocess.run(
                ["python", "-m", "aicode", "--message-file", temp_path],
                capture_output=True,
                text=True,
                check=False,
                shell=True,
            )

            stdout = result.stdout
            stderr = result.stderr
            assert stdout is not None
            assert stderr is not None

            # Check that the output contains the --message-file argument with the correct path
            self.assertIn(f"--message-file {temp_path}", result.stdout)

            # Verify the command executed successfully
            self.assertEqual(0, result.returncode)
        finally:
            # Clean up the temporary file

            # print out stdout and stderr for debugging
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
