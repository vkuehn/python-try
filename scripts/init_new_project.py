"""Initialize a new project from this template with rollback safety."""

import importlib.util
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- Custom Exceptions (Fixes TRY003) ---


class ProjectInitError(Exception):
    """Base exception for project initialization errors."""


class DependencyNotFoundError(ProjectInitError):
    """Raised when a required external tool or library is missing."""

    def __init__(self, name: str, instructions: str = "") -> None:
        msg = f"Required dependency not found: {name}. {instructions}"
        super().__init__(msg)


class InputValidationError(ProjectInitError):
    """Raised when user input fails validation."""


class FileOperationError(ProjectInitError):
    """Raised when file system operations fail."""


# --- Helper Functions ---


def _remove_readonly(func: callable, path: str, _) -> None:  # type: ignore
    """Error handler for shutil.rmtree to remove read-only files (Windows fix)."""
    try:
        os_chmod = importlib.import_module("os").chmod
        os_chmod(path, stat.S_IWRITE)
        func(path)
    except ImportError, OSError:
        pass


def _safe_rmtree(path: Path) -> None:
    """Robustly remove a directory tree."""
    if path.exists():
        shutil.rmtree(path, onerror=_remove_readonly)


def _resolve_executable(name: str) -> Path:
    """Resolve an executable path."""
    resolved = shutil.which(name)
    if not resolved:
        raise DependencyNotFoundError(name)
    return Path(resolved).absolute()


# --- Main Logic Class (Fixes C901) ---


@dataclass
class ProjectInitializer:
    """Handles the initialization of a new project from the template."""

    author: str
    email: str
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.resolve())
    git_path: Path = field(init=False)
    uv_path: Path = field(init=False)
    # Rollback state
    _steps_taken: list[str] = field(default_factory=list)

    @property
    def git_dir(self) -> Path:
        return self.project_root / ".git"

    @property
    def backup_dir(self) -> Path:
        return self.project_root / ".git_backup"

    @property
    def pyproject_file(self) -> Path:
        return self.project_root / "pyproject.toml"

    @property
    def pyproject_backup(self) -> Path:
        return self.project_root / "pyproject.toml.bak"

    def check_dependencies(self) -> None:
        """Verify all required tools and libraries are present."""
        # 1. Check Python libs
        if not importlib.util.find_spec("tomli_w") or not importlib.util.find_spec("tomllib"):
            msg = "Run 'pip install tomli-w' (requires Python 3.11+ for tomllib)."
            raise DependencyNotFoundError("tomli_w/tomllib", msg)

        # 2. Check System tools
        self.git_path = _resolve_executable("git")
        self.uv_path = _resolve_executable("uv")

        if not self.pyproject_file.exists():
            msg = f"pyproject.toml not found at {self.pyproject_file}"
            raise FileOperationError(msg)

    def get_user_input(self) -> tuple[str, str]:
        """Gather project details from user."""
        name = input("🔗 New project name (Enter): ").strip()
        if len(name) < 3:
            msg = f"Name '{name}' is too short (min 3 chars)."
            raise InputValidationError(msg)

        remote = input("🔗 New remote URL (Enter to skip): ").strip()
        return name, remote

    def backup_git_history(self) -> None:
        """Move existing .git folder to backup location."""
        if not self.git_dir.exists():
            return

        print("📦 Backing up .git...")
        if self.backup_dir.exists():
            _safe_rmtree(self.backup_dir)

        try:
            self.git_dir.rename(self.backup_dir)
            self._steps_taken.append("git_backup")
        except OSError as e:
            msg = f"Failed to backup .git: {e}"
            raise FileOperationError(msg) from e

    def update_pyproject(self, new_name: str, remote_url: str) -> None:
        """Modify pyproject.toml with new metadata."""
        import tomllib  # type: ignore

        import tomli_w  # type: ignore

        print("📝 Updating pyproject.toml...")
        # Create backup
        shutil.copy(self.pyproject_file, self.pyproject_backup)
        self._steps_taken.append("pyproject_mod")

        with self.pyproject_file.open("rb") as f:
            config = tomllib.load(f)

        # Modify structure
        project = config.get("project", {})
        project["name"] = new_name
        project["authors"] = [{"name": self.author, "email": self.email}]

        if "urls" not in project:
            project["urls"] = {}

        if remote_url:
            project["urls"]["Repository"] = remote_url

        # Save
        with self.pyproject_file.open("wb") as f:
            tomli_w.dump(config, f)

    def reinitialize_git(self, remote_url: str, new_name: str) -> None:
        """Initialize fresh git repo and commit."""
        print("🌱 Initializing Git repository...")

        # Clean old venv if exists
        venv_dir = self.project_root / ".venv"
        if venv_dir.exists():
            _safe_rmtree(venv_dir)

        # Init
        self._run([str(self.git_path), "init", "-b", "main"])
        self._steps_taken.append("git_inited")

        if remote_url:
            self._run([str(self.git_path), "remote", "add", "origin", remote_url])

        print("💾 Creating initial commit...")
        self._run([str(self.git_path), "add", "."])
        self._run([str(self.git_path), "commit", "-m", f"Initial commit for {new_name}"])

    def install_environment(self) -> None:
        """Sync uv environment and install hooks."""
        print("🪝  Rebuilding environment and hooks...")
        self._run([str(self.uv_path), "sync", "--frozen"])
        self._run([str(self.uv_path), "run", "pre-commit", "install"])

    def cleanup_success(self) -> None:
        """Remove backups after successful run."""
        if self.backup_dir.exists():
            _safe_rmtree(self.backup_dir)
        if self.pyproject_backup.exists():
            self.pyproject_backup.unlink()
        print("\n✨ Done! Start your shell with: source .venv/bin/activate")

    def rollback(self) -> None:
        """Restore state based on steps taken."""
        print("\n🔄 Starting rollback due to failure...")

        # 1. Restore Git
        if "git_inited" in self._steps_taken and self.git_dir.exists():
            _safe_rmtree(self.git_dir)

        if "git_backup" in self._steps_taken and self.backup_dir.exists():
            if self.git_dir.exists():
                _safe_rmtree(self.git_dir)
            self.backup_dir.rename(self.git_dir)
            print("✅ Restored original .git directory.")

        # 2. Restore pyproject.toml
        if "pyproject_mod" in self._steps_taken and self.pyproject_backup.exists():
            if self.pyproject_file.exists():
                self.pyproject_file.unlink()
            self.pyproject_backup.rename(self.pyproject_file)
            print("✅ Restored original pyproject.toml.")

    def _run(self, cmd: list[str]) -> None:
        """Execute subprocess command securely."""
        subprocess.run(cmd, cwd=self.project_root, check=True, shell=False)  # noqa: S603

    def execute(self) -> None:
        """Orchestrate the initialization process."""
        self.check_dependencies()

        try:
            new_name, remote_url = self.get_user_input()

            print(f"🚀 Initializing project as '{new_name}'")
            print("⚠️  WARNING: This will delete Git history and .venv!")
            if input("Continue? (y/n): ").lower() != "y":
                print("Aborted.")
                return

            self.backup_git_history()
            self.update_pyproject(new_name, remote_url)
            self.reinitialize_git(remote_url, new_name)
            self.install_environment()
            self.cleanup_success()

        except (subprocess.CalledProcessError, ProjectInitError, OSError) as e:
            print(f"\n💥 ERROR: {e}")
            self.rollback()
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user.")
            self.rollback()
            sys.exit(1)


def main() -> None:
    """Entry point."""
    # Local import to avoid global scope pollution if module used elsewhere
    try:
        from check_git_config import check_git_config
    except ImportError:
        print("❌ 'check_git_config.py' module not found.")
        sys.exit(1)

    print("🔍 Checking Git configuration...")
    git_config = check_git_config()

    if not git_config:
        print("❌ Git configuration check failed.")
        sys.exit(1)

    user_name = git_config.get("username", "Unknown")
    user_email = git_config.get("email", "unknown@example.com")

    print("✅ Git configuration looks good.")

    initializer = ProjectInitializer(author=user_name, email=user_email)
    initializer.execute()


if __name__ == "__main__":
    main()
