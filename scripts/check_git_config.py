"""this script os independed for Windows, MAc and Linux if git is configured properly.

It will check if Lf or CrLf is used properly in commit messages
"""

import logging
import platform
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_git_config() -> bool:
    """Check if Git is configured to handle line endings correctly.

    Returns:
    -------
    bool
        True if Git is configured correctly, False otherwise.
    """
    try:
        import subprocess

        result = subprocess.run(
            ["git", "config", "--get", "core.autocrlf"], capture_output=True, text=True, check=True, shell=False
        )
        autocrlf = result.stdout.strip().lower()
        if platform.system() == "Windows" and autocrlf != "true":
            print("ERROR: On Windows, please set git config core.autocrlf to true.")
            return False
        elif platform.system() != "Windows" and autocrlf != "input":
            print("ERROR: On Unix-like systems, please set git config core.autocrlf to input.")
            return False
    except FileNotFoundError:
        print("ERROR: Git executable not found in PATH")
        return False
    except Exception as e:
        print(f"ERROR: Unable to check git configuration: {e}")
        return False

    return True


if __name__ == "__main__":
    if not check_git_config():
        logger.error("Git configuration check failed.")
        sys.exit(1)
    else:
        logger.info("Git configuration is correct.")
