"""Initialize a new project from this with rollback safety."""

import shutil
import subprocess
import sys
from pathlib import Path

from check_git_config import check_git_config


def _resolve_executable(name: str) -> str:
    """Resolve an executable path and verify it exists (Bandit S607 fix)."""
    resolved = shutil.which(name)
    if not resolved:
        msg = f"Required executable not found on PATH: {name}"
        raise FileNotFoundError(msg)
    return str(Path(resolved).absolute())


def _run_cmd(cmd: list[str], cwd: Path) -> None:
    """Run a subprocess command with security bypass for known tools."""
    subprocess.run(cmd, cwd=cwd, check=True, shell=False)  # noqa: S603


def migrate_pyproject(pyproject_path: Path, new_name: str, new_author: str, new_email: str):
    """Update pyproject.toml with new project name and author info."""
    if not pyproject_path.exists():
        return print("❌ pyproject.toml not found.")

    # 1. Read and Identify Old Name
    lines = pyproject_path.read_text().splitlines()
    old_name = None
    for line in lines:
        if line.startswith('name = "'):
            old_name = line.split('"')[1]
            break

    if not old_name:
        return print("❌ Could not determine old project name.")

    # 2. Reconstruct pyproject.toml line-by-line
    new_lines = []
    for line in lines:
        if line.strip().startswith('name = "'):
            new_lines.append(f'name = "{new_name}"')
        elif line.strip().startswith('name = "') and "authors" in "".join(new_lines[-5:]):
            # This handles the name inside the authors block specifically
            new_lines.append(f'    {{ name = "{new_author}", email = "{new_email}" }},')
        elif "email =" in line and "name =" in line and "[" in "".join(new_lines[-2:]):
            # Simplified author replacement for standard uv init layout
            new_lines.append(f'authors = [{{ name = "{new_author}", email = "{new_email}" }}]')
        else:
            new_lines.append(line)

    pyproject_path.write_text("\n".join(new_lines) + "\n")
    print("✅ Metadata updated in pyproject.toml")

    # 5. Refresh uv state
    lock_file = pyproject_path / "uv.lock"
    if lock_file.exists():
        lock_file.unlink()
        print("🗑️  Old lockfile removed. Run 'uv sync' to regenerate.")


def init_new_project(new_author: str, new_email: str) -> None:
    """Main entry point for project initialization."""
    project_root: Path = Path(__file__).parent.parent
    git_dir: Path = project_root / ".git"
    backup_dir: Path = project_root / ".git_backup"
    venv_dir: Path = project_root / ".venv"
    new_project_name: str = project_root.name
    pyproject_backup_path = project_root / "pyproject.toml.bak"

    try:
        git_path: str = _resolve_executable("git")
        uv_path: str = _resolve_executable("uv")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print(f"🚀 Initializing project from '{new_project_name}' template")
    print("⚠️  WARNING: This will delete the Git history and .venv!")
    if input("Continue? (y/n): ").lower() != "y":
        print("Aborted.")
        sys.exit(0)

    steps: list[str] = []

    try:
        # 1. Backup Git
        if git_dir.exists():
            print(f"📦 Backing up .git -> {backup_dir.name}...")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            git_dir.rename(backup_dir)
            steps.append("git_backup")

        # 2. Update metadata (pyproject.toml)
        pyproject_path = project_root / "pyproject.toml"
        if not pyproject_path.exists():
            print("❌ pyproject.toml not found. Cannot update project metadata.")
            sys.exit(1)
        else:
            print("Backing up and updating pyproject.toml metadata...")
            # copy pyproject.toml to backup before modifying
            shutil.copy(pyproject_path, pyproject_backup_path)
        migrate_pyproject(pyproject_path, new_project_name, new_author, new_email)

        # 3. Remove old .venv (because of old name in prompt)
        if venv_dir.exists():
            print("🧹 Removing old virtual environment...")
            shutil.rmtree(venv_dir)

        # 4. Re-initialize Git
        print("🌱 Initializing new Git repository...")
        _run_cmd([git_path, "init", "-b", "main"], cwd=project_root)
        steps.append("git_inited")

        # 5. Set remote
        remote_url = input("🔗 New remote URL (Enter to skip): ").strip()
        if remote_url:
            _run_cmd([git_path, "remote", "add", "origin", remote_url], cwd=project_root)

        # 6. Initial commit
        print("💾 Creating initial commit...")
        _run_cmd([git_path, "add", "."], cwd=project_root)
        _run_cmd([git_path, "commit", "-m", f"Initial commit for {new_project_name}"], cwd=project_root)

        # 7. Rebuild environment & hooks
        print("🪝  Rebuilding environment and hooks (uv sync)...")
        _run_cmd([uv_path, "sync", "--frozen"], cwd=project_root)
        _run_cmd([uv_path, "run", "pre-commit", "install"], cwd=project_root)

        # Final cleanup
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        print("\n✨ Done! Start your new shell with: source .venv/bin/activate")

    except (subprocess.CalledProcessError, Exception) as e:
        print(f"\n💥 ERROR: {e}")
        _rollback(steps, git_dir, backup_dir)
        sys.exit(1)


def _rollback(steps: list[str], git_dir: Path, backup_dir: Path) -> None:
    """Reverts Git changes to restore the original state."""
    print("🔄 Starting rollback...")
    if "git_inited" in steps and git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)

    if "git_backup" in steps and backup_dir.exists():
        backup_dir.rename(git_dir)
        print("✅ Original .git folder has been restored.")
    print("\n❌ Initialization failed. Original state restored.")


if __name__ == "__main__":
    print("🔍 Checking Git configuration...")
    git_config = check_git_config()
    if not git_config:
        print("❌ Git configuration check failed. Please fix the issues and try again.")
        sys.exit(1)
    user_name = git_config.get("username")
    user_email = git_config.get("email")
    print("✅ Git configuration looks good. using the following:")
    print(f"👤 Git user.name: {user_name}")
    print(f"📧 Git user.email: {user_email}")
    init_new_project(new_author=user_name, new_email=user_email)
