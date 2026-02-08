"""this script os independed for Windows, MAc and Linux if git is configured properly.

It will check if Lf or CrLf is used properly in commit messages
"""

import logging
import platform
import sys

logger = logging.getLogger("check_git_config")
logging.basicConfig(level=logging.INFO)


def check_user() -> bool:
    """Check if git global config has a user.name configuration."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "config", "--get", "user.name"], capture_output=True, text=True, check=False, shell=False
        )
        if result.returncode != 0 or not result.stdout.strip():
            print("ERROR: Git user.name is not configured. Please run: git config --global user.name 'Your Name'")
            return False
    except FileNotFoundError:
        print("ERROR: Git executable not found in PATH")
        return False
    except Exception as e:
        print(f"ERROR: Unable to check git configuration: {e}")
        return False

    return True


def check_email() -> bool:
    """Check if git global config has a user.email configuration."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "config", "--get", "user.email"], capture_output=True, text=True, check=False, shell=False
        )
        if result.returncode != 0 or not result.stdout.strip():
            print(
                "ERROR: Git user.email is not configured. Please run: git config --global user.email 'your.email@example.com'"
            )
            return False
    except FileNotFoundError:
        print("ERROR: Git executable not found in PATH")
        return False
    except Exception as e:
        print(f"ERROR: Unable to check git configuration: {e}")
        return False

    return True


def check_autocrlf() -> bool:
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


def check_git_config() -> bool:
    """Check if Git is configured properly for user.name, user.email, and core.autocrlf."""
    if not check_user():
        return False
    if not check_email():
        return False
    return check_autocrlf()


if __name__ == "__main__":
    if not check_user():
        logger.error("Git user.name config check failed.")
        sys.exit(1)
    else:
        logger.info("Git user.name is configured.")
    if not check_email():
        logger.error("Git user.email config check failed.")
        sys.exit(1)
    else:
        logger.info("Git user.email is configured.")
    if not check_autocrlf():
        logger.error("Git crlf config check failed.")
        sys.exit(1)
    else:
        logger.info("Git crlf is correct.")
