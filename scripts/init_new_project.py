"""Initialize a new project from this template with rollback safety."""

import contextlib
import importlib.util
import logging
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import tomlkit
from check_git_config import check_git_config

# Setup logging in your initializer or main():
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class ProjectInitError(Exception):
    """Base exception for project initialization errors."""


@dataclass
class ProjectConfig:
    """Configuration for pyproject.toml updates."""

    name: str
    authors: list[dict[str, str]]
    version: str
    description: str
    documentation_url: str = ""
    repository_url: str = ""


class DependencyNotFoundError(ProjectInitError):
    """Raised when a required external tool or library is missing."""

    def __init__(self, name: str, instructions: str = "") -> None:
        """Initialize with the missing dependency name and optional instructions."""
        msg = f"Required dependency not found: {name}. {instructions}"
        super().__init__(msg)


class InputValidationError(ProjectInitError):
    """Raised when user input fails validation."""


class FileOperationError(ProjectInitError):
    """Raised when file system operations fail."""


# --- Helper Functions ---
def _delete_path(path: Path) -> None:
    """Robustly remove a directory tree."""
    if not path.exists():
        return

    if path.is_file():
        path.unlink()
        return

    for item in path.rglob("*"):
        try:
            if item.is_file():
                item.chmod(stat.S_IWRITE)
                item.unlink()
            elif item.is_dir() and not any(item.iterdir()):
                item.rmdir()
        except OSError:
            pass
    with contextlib.suppress(OSError):
        path.rmdir()


class ProjectInitializer:
    """Handles the initialization of a new project from the template."""

    def __init__(self) -> None:
        """Initialize the project initializer with default paths and state tracking."""
        self.project_root = Path(__file__).parent.resolve()
        self.git_path: Path | None = None
        self.uv_path: Path | None = None
        # Rollback state
        self._steps_taken: list[str] = []

    @property
    def git_dir(self) -> Path:
        """Git directory path."""
        return self.project_root / ".git"

    @property
    def git_backup_dir(self) -> Path:
        """Git backup directory path."""
        return self.project_root / ".git_backup"

    @property
    def pyproject_file(self) -> Path:
        """Pyproject.toml file path."""
        return self.project_root / "pyproject.toml"

    @property
    def pyproject_file_backup(self) -> Path:
        """Pyproject.toml backup file path."""
        return self.pyproject_file + ".bak"

    def check_dependencies(self) -> None:
        """Verify all required tools and libraries are present."""
        # 1. Check Python libs
        if not (importlib.util.find_spec("tomlkit")):
            msg = "Run 'uv sync --frozen' to install required Python libraries."
            raise DependencyNotFoundError("tomlkit", msg)

        # 2. Check System tools
        self.git_path = self._resolve_executable("git")
        self.uv_path = self._resolve_executable("uv")

        if not self.pyproject_file.exists():
            msg = f"pyproject.toml not found at {self.pyproject_file}"
            raise FileOperationError(msg)

    def backup_git_history(self) -> None:
        """Move existing .git folder to backup location."""
        if not self.git_dir.exists():
            return

        logger.warning("⚠️  This will delete Git history and .venv!")
        if input("Continue? (y/n): ").lower() != "y":
            logger.info("Aborted.")
            self._exit_on_error(InputValidationError("User decided to stop at git history deletion"), exit_code=130)

        print("📦 Backing up .git...")
        if self.git_backup_dir.exists():
            _delete_path(self.git_backup_dir)

        try:
            self.git_dir.rename(self.git_backup_dir)
            self._steps_taken.append("git_backup")
        except OSError as e:
            msg = f"Failed to backup .git: {e}"
            raise FileOperationError(msg) from e

    def backup_pyproject_toml(self, file_path: Path) -> None:
        """Create a backup of the pyproject.toml file.

        Parameters
        ----------
        file_path : str
            Path to the pyproject.toml file to backup.
        """
        with open(file_path) as original_file, open(self.pyproject_file_backup, "w") as backup_file:
            backup_file.write(original_file.read())
        self._steps_taken.append("pyproject_mod")
        print(f"Backup created at {self.pyproject_file_backup}")

    def _exit_on_error(self, error: Exception, exit_code: int = 1) -> None:
        """Log error, rollback, and exit cleanly."""
        logger.error(f"ERROR: {error}")
        self.rollback()
        sys.exit(exit_code)

    def _get_user_input(self, user_email: str, user_name: str) -> ProjectConfig:
        name = input("🔗 New project name (Enter): ").strip()
        author = input(f"🔗 Author name [{user_name}]: ").strip() or user_name
        email = input(f"🔗 Author email [{user_email}]: ").strip() or user_email

        # Validate inputs
        if not name:
            self._exit_on_error(InputValidationError("Project Name"), exit_code=130)
        if not author:
            self._exit_on_error(InputValidationError("Author name"), exit_code=130)
        if not email:
            self._exit_on_error(InputValidationError("Author email"), exit_code=130)

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

    def _resolve_executable(self, name: str) -> Path:
        """Resolve an executable path."""
        resolved = shutil.which(name)
        if not resolved:
            raise DependencyNotFoundError(name)
        return Path(resolved).absolute()

    def reinitialize_git(self, remote_url: str, new_name: str) -> None:
        """Initialize fresh git repo and commit."""
        print("🌱 Initializing Git repository...")

        # Clean old venv if exists
        venv_dir = self.project_root / ".venv"
        if venv_dir.exists():
            _delete_path(venv_dir)

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
        if self.git_backup_dir.exists():
            _delete_path(self.git_backup_dir)
        if self.pyproject_file_backup.exists():
            self.pyproject_file_backup.unlink()
        print("\n✨ Done! Start your shell with: source .venv/bin/activate")

    def rollback(self) -> None:
        """Restore state based on steps taken."""
        print("\n🔄 Starting rollback due to failure...")

        # 1. Restore Git
        if "git_inited" in self._steps_taken and self.git_dir.exists():
            _delete_path(self.git_dir)

        if "git_backup" in self._steps_taken and self.git_backup_dir.exists():
            if self.git_dir.exists():
                _delete_path(self.git_dir)
            self.git_backup_dir.rename(self.git_dir)
            print("✅ Restored original .git directory.")

        # 2. Restore pyproject.toml
        if "pyproject_mod" in self._steps_taken and self.pyproject_file_backup.exists():
            if self.pyproject_file.exists():
                self.pyproject_file.unlink()
            self.pyproject_file_backup.rename(self.pyproject_file)
            print("✅ Restored original pyproject.toml.")

    def _run(self, cmd: list[str]) -> None:
        """Execute subprocess command securely."""
        subprocess.run(cmd, cwd=self.project_root, check=True, shell=False)  # noqa: S603

    def update_pyproject_toml(self, config: ProjectConfig) -> None:
        """Update authors, version, and description in pyproject.toml.

        Parameters
        ----------
        config : ProjectConfig
            Configuration object containing all project metadata.
        """
        with open(self.pyproject_file) as file:
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
        with open(self.pyproject_file, "w") as file:
            tomlkit.dump(pyproject_data, file)

    def execute(self) -> None:
        """Orchestrate the initialization process."""
        self.check_dependencies()

        # Ask User for new ProjectConfig details
        print("🔍 Checking Git global configuration...")
        git_config = check_git_config()

        if not git_config:
            print("❌ Git global configuration check failed.")
            sys.exit(1)

        user_name = git_config.get("username")
        user_email = git_config.get("email")

        print("✅ Git configuration looks good.Continue with project initialization.")

        try:
            config = self._get_user_input(user_email, user_name)

            logger.info(f"🚀 Initializing project as '{config.name}'")

            self.backup_git_history()
            self.backup_pyproject_toml(self.pyproject_file)
            self.update_pyproject_toml(config)
            self.reinitialize_git(config.repository_url, config.name)
            self.install_environment()
            self.cleanup_success()

        except (subprocess.CalledProcessError, ProjectInitError, OSError) as e:
            print(f"\n💥 ERROR: {e}")
            self.rollback()
            self._exit_on_error(ProjectInitError("User interrupted"), exit_code=130)
        except KeyboardInterrupt:
            logger.info("🛑 Interrupted by user.")
            self._exit_on_error(KeyboardInterrupt("User interrupted"), exit_code=130)


if __name__ == "__main__":
    initializer = ProjectInitializer()
    initializer.execute()
