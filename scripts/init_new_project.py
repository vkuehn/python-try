"""Initialize a new project from this template.

This script removes the existing `.git` history and initializes a fresh git
repository. Optionally, it can attach a new `origin` remote.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def _resolve_executable(name: str) -> str:
    resolved = shutil.which(name)
    if resolved is None:
        msg = f"Required executable not found on PATH: {name}"
        raise FileNotFoundError(msg)
    return resolved


def init_new_project() -> None:
    """Remove the existing git history and initialize a fresh repository."""
    project_root = Path(__file__).parent.parent
    git_dir = project_root / ".git"

    git = _resolve_executable("git")
    uv = _resolve_executable("uv")

    print("⚠️  WARNING: This will delete the entire git history of this project!")
    print("    It is intended for starting a NEW project from this template.")
    confirm = input("Are you sure you want to continue? (y/n): ").lower()

    if confirm != "y":
        print("Aborting.")
        sys.exit(0)

    # 1. Remove old git history
    if git_dir.exists():
        print(f"🔥 Removing old git history at {git_dir}...")
        shutil.rmtree(git_dir, ignore_errors=True)

    # 2. Initialize new git repo
    print("🌱 Initializing new git repository...")
    subprocess.run([git, "init", "-b", "main"], cwd=project_root, check=True)  # noqa: S603

    # 3. Ask for new remote
    new_remote = input(
        "🔗 Enter new git remote URL (e.g., git@github.com:user/repo.git) or press Enter to skip: "
    ).strip()

    if new_remote:
        subprocess.run([git, "remote", "add", "origin", new_remote], cwd=project_root, check=True)  # noqa: S603
        print(f"✅ Remote 'origin' set to: {new_remote}")
    else:
        print("INFO: Skipping remote setup. You can add it later with 'git remote add origin <url>'")

    # 4. Initial commit
    print("📦 Creating initial commit...")
    subprocess.run([git, "add", "."], cwd=project_root, check=True)  # noqa: S603
    subprocess.run(  # noqa: S603
        [git, "commit", "-m", "Initial commit from python-try template"],
        cwd=project_root,
        check=True,
    )

    # 5. Re-install hooks (since .git was deleted, hooks are gone)
    print("🪝  Re-installing git hooks...")
    # Ensure uv is ready
    subprocess.run([uv, "sync", "--frozen"], cwd=project_root, check=False)  # noqa: S603
    subprocess.run([uv, "run", "pre-commit", "install"], cwd=project_root, check=False)  # noqa: S603

    # Re-run your custom hook setup script
    setup_hook = project_root / "scripts" / "setup_hook_commit_message.py"
    if setup_hook.exists():
        subprocess.run([uv, "run", str(setup_hook)], cwd=project_root)  # noqa: S603

    print("\n✨ Project ready! You can now push to your new origin.")


if __name__ == "__main__":
    init_new_project()
