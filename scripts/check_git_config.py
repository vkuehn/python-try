"""this script os independed for Windows, MAc and Linux if git is configured properly.

It will check if Lf or CrLf is used properly in commit messages
"""

import logging
import platform
import sys

logger = logging.getLogger("check_git_config")
logging.basicConfig(level=logging.INFO)

username = "Hopefully not this"
email = "Hopefully not this either"
crlf = "Must be OK"


def check_user() -> str:
    """Check if git global config has a user.name configuration."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "config", "--get", "user.name"], capture_output=True, text=True, check=False, shell=False
        )
        if result.returncode != 0 or not result.stdout.strip():
            print("ERROR: Git user.name is not configured. Please run: git config --global user.name 'Your Name'")
            return ""
        else:
            username = result.stdout.strip()
            print(f"Git user.name is configured as: {username}")
            return username
    except FileNotFoundError:
        print("ERROR: Git executable not found in PATH")
        return False
    except Exception as e:
        print(f"ERROR: Unable to check git configuration: {e}")
        return False


def check_email() -> str:
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
            return ""
        else:
            email = result.stdout.strip()
            print(f"Git user.email is configured as: {email}")
            return email
    except FileNotFoundError:
        print("ERROR: Git executable not found in PATH")
        return ""
    except Exception as e:
        print(f"ERROR: Unable to check git configuration: {e}")
        return ""


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
        else:
            print(f"Git core.autocrlf is configured as: {autocrlf} (looks good for {platform.system()})")
    except FileNotFoundError:
        print("ERROR: Git executable not found in PATH")
        return False
    except Exception as e:
        print(f"ERROR: Unable to check git configuration: {e}")
        return False

    return True


def check_git_config() -> dict[str, str]:
    """Check if Git is configured properly for user.name, user.email, and core.autocrlf."""
    username = check_user()
    if not username:
        return {}
    email = check_email()
    if not email:
        return {}
    if not check_autocrlf():
        return {}
    return {"username": username, "email": email}


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
