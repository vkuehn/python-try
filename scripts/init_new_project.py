"""Initialize a new project from this template.

This script removes the existing `.git` history and initializes a fresh git
repository. Optionally, it can attach a new `origin` remote.
"""

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import tomlkit


@dataclass
class ProjectConfig:
    """Configuration for pyproject.toml updates."""

    name: str
    authors: list[dict[str, str]]
    version: str
    description: str
    documentation_url: str = ""
    repository_url: str = ""


def _resolve_executable(name: str) -> str:
    resolved = shutil.which(name)
    if resolved is None:
        msg = f"Required executable not found on PATH: {name}"
        raise FileNotFoundError(msg)
    return resolved


def _update_pyproject_toml(config: ProjectConfig, project_root: Path) -> None:
    """Update authors, version, and description in pyproject.toml.

    Parameters
    ----------
    config : ProjectConfig
        Configuration object containing all project metadata.
    """
    pyproject_file = project_root / "pyproject.toml"
    with open(pyproject_file) as file:
        pyproject_data = tomlkit.load(file)

    # Update the project owner, version, and description

    authors_array = tomlkit.array()
    for author in config.authors:
        inline_table = tomlkit.inline_table()
        inline_table.update(author)
        authors_array.append(inline_table)

    pyproject_data["project"]["name"] = config.name
    pyproject_data["project"]["authors"] = authors_array
    pyproject_data["project"]["version"] = config.version
    pyproject_data["project"]["description"] = config.description

    # Update project CONFIG
    pyproject_data["project"]["urls"]["Documentation"] = config.documentation_url
    pyproject_data["project"]["urls"]["Repository"] = config.repository_url

    # Write the updated data back to the pyproject.toml file
    with open(pyproject_file, "w") as file:
        tomlkit.dump(pyproject_data, file)


def _get_user_input(user_email: str, user_name: str) -> ProjectConfig:
    name = input("🔗 New project name (Enter): ").strip()
    author = input(f"🔗 Author name [{user_name}]: ").strip() or user_name
    email = input(f"🔗 Author email [{user_email}]: ").strip() or user_email

    if not name:
        sys.exit(130)
    if not author:
        sys.exit(130)
    if not email:
        sys.exit(130)

    repository_url = input("🔗 Repository URL : ").strip()

    config = ProjectConfig(
        name=name,
        authors=[{"name": author, "email": email}],
        version="0.0.1",
        description="A sample Python project using Poetry.",
        documentation_url=repository_url + "/docs",
        repository_url=repository_url,
    )

    return config


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

    # Get current git user info for pre-filling prompts
    try:
        user_name = subprocess.check_output([git, "config", "user.name"], text=True).strip()  # noqa: S603
        user_email = subprocess.check_output([git, "config", "user.email"], text=True).strip()  # noqa: S603
    except subprocess.CalledProcessError:
        user_name = "none"
        user_email = "none"

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

    # 6. Update pyproject.toml with new project metadata
    print("📝 Updating pyproject.toml with new project metadata...")
    config = _get_user_input(user_email=user_email, user_name=user_name)
    _update_pyproject_toml(config=config, project_root=project_root)

    # Re-run your custom hook setup script
    setup_hook = project_root / "scripts" / "setup_hook_commit_message.py"
    if setup_hook.exists():
        subprocess.run([uv, "run", str(setup_hook)], cwd=project_root)  # noqa: S603

    print("\n✨ Project ready! You can now push to your new origin.")


if __name__ == "__main__":
    init_new_project()
