"""Initialize a new project from this template with rollback safety."""

import shutil
import subprocess
import sys
from pathlib import Path


def _resolve_executable(name: str) -> str:
    """Resolve an executable path and verify it exists."""
    resolved = shutil.which(name)
    if not resolved:
        msg = f"Required executable not found on PATH: {name}"
        raise FileNotFoundError(msg)
    return str(Path(resolved).absolute())


def _run_cmd(cmd: list[str], cwd: Path) -> None:
    """Run a subprocess command with fixed security settings."""
    # shell=False ist Standard, aber explizit sicherer gegen Injection
    subprocess.run(cmd, cwd=cwd, check=True, shell=False)  # noqa: S603


def init_new_project() -> None:
    """Main entry point for project initialization."""
    project_root: Path = Path(__file__).parent.parent
    git_dir: Path = project_root / ".git"
    backup_dir: Path = project_root / ".git_backup"

    try:
        git_path: str = _resolve_executable("git")
        uv_path: str = _resolve_executable("uv")
    except FileNotFoundError as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)

    print("⚠️  WARNUNG: Dies wird die gesamte Git-Historie löschen!")
    confirm: str = input("Fortfahren? (y/n): ").lower()
    if confirm != "y":
        print("Abbruch durch Nutzer.")
        sys.exit(0)

    steps: list[str] = []

    try:
        # 1. Backup
        if git_dir.exists():
            print(f"📦 Erstelle Backup von .git -> {backup_dir.name}...")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            git_dir.rename(backup_dir)
            steps.append("backup_created")

        # 2. Git Init
        print("🌱 Initialisiere neues Git-Repository...")
        _run_cmd([git_path, "init", "-b", "main"], cwd=project_root)
        steps.append("git_inited")

        # 3. Remote
        new_remote: str = input("🔗 Neuer Git Remote URL (Enter zum Überspringen): ").strip()
        if new_remote:
            _run_cmd([git_path, "remote", "add", "origin", new_remote], cwd=project_root)
            print("✅ Remote gesetzt.")

        # 4. Initial Commit
        print("💾 Erstelle Initial Commit...")
        _run_cmd([git_path, "add", "."], cwd=project_root)
        _run_cmd([git_path, "commit", "-m", "Initial commit from template"], cwd=project_root)

        # 5. Tooling
        print("🪝  Installiere Hooks und Abhängigkeiten...")
        _run_cmd([uv_path, "sync", "--frozen"], cwd=project_root)
        _run_cmd([uv_path, "run", "pre-commit", "install"], cwd=project_root)

        # 6. Cleanup Backup
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        print("\n✨ Projekt erfolgreich initialisiert!")

    except (subprocess.CalledProcessError, Exception) as e:
        print(f"\n💥 FEHLER: {e}")
        _rollback(steps, git_dir, backup_dir)
        sys.exit(1)


def _rollback(steps: list[str], git_dir: Path, backup_dir: Path) -> None:
    """Revert changes if something went wrong."""
    print("🔄 Starte Rollback...")
    if "git_inited" in steps and git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)

    if "backup_created" in steps and backup_dir.exists():
        backup_dir.rename(git_dir)
        print("✅ Ursprünglicher .git-Ordner wurde wiederhergestellt.")
    print("\n❌ System ist im Ursprungszustand.")


if __name__ == "__main__":
    init_new_project()
