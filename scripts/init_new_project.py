"""Initialize a new project from this with rollback safety."""

import re
import shutil
import subprocess
import sys
from pathlib import Path


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


def update_project_metadata(project_root: Path, new_name: str) -> None:
    """Updates the project name in pyproject.toml to fix the .venv prompt."""
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        print(f"📝 Aktualisiere Projektname in pyproject.toml auf '{new_name}'...")
        content = pyproject.read_text(encoding="utf-8")
        # Ersetzt 'name = "..." ' in der [project] Sektion
        new_content = re.sub(r'^name\s*=\s*".*?"', f'name = "{new_name}"', content, flags=re.MULTILINE)
        pyproject.write_text(new_content, encoding="utf-8")


def init_new_project() -> None:
    """Main entry point for project initialization."""
    project_root: Path = Path(__file__).parent.parent
    git_dir: Path = project_root / ".git"
    backup_dir: Path = project_root / ".git_backup"
    venv_dir: Path = project_root / ".venv"
    new_project_name: str = project_root.name

    try:
        git_path: str = _resolve_executable("git")
        uv_path: str = _resolve_executable("uv")
    except FileNotFoundError as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)

    print(f"🚀 Initialisiere neues Projekt: '{new_project_name}'")
    print("⚠️  WARNUNG: Dies wird die Git-Historie und .venv löschen!")
    if input("Fortfahren? (y/n): ").lower() != "y":
        print("Abbruch.")
        sys.exit(0)

    steps: list[str] = []

    try:
        # 1. Backup Git
        if git_dir.exists():
            print(f"📦 Backup von .git -> {backup_dir.name}...")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            git_dir.rename(backup_dir)
            steps.append("git_backup")

        # 2. Metadaten anpassen (pyproject.toml)
        update_project_metadata(project_root, new_project_name)

        # 3. Alte .venv entfernen (wegen altem Namen im Prompt)
        if venv_dir.exists():
            print("🧹 Entferne alte virtuelle Umgebung...")
            shutil.rmtree(venv_dir)

        # 4. Git neu initialisieren
        print("🌱 Initialisiere neues Git-Repository...")
        _run_cmd([git_path, "init", "-b", "main"], cwd=project_root)
        steps.append("git_inited")

        # 5. Remote setzen
        remote_url = input("🔗 Neuer Remote URL (Enter zum Überspringen): ").strip()
        if remote_url:
            _run_cmd([git_path, "remote", "add", "origin", remote_url], cwd=project_root)

        # 6. Initial Commit
        print("💾 Erstelle Initial Commit...")
        _run_cmd([git_path, "add", "."], cwd=project_root)
        _run_cmd([git_path, "commit", "-m", f"Initial commit for {new_project_name}"], cwd=project_root)

        # 7. Environment & Hooks neu aufbauen
        print("🪝  Baue Environment und Hooks neu auf (uv sync)...")
        _run_cmd([uv_path, "sync", "--frozen"], cwd=project_root)
        _run_cmd([uv_path, "run", "pre-commit", "install"], cwd=project_root)

        # Finaler Cleanup
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        print("\n✨ Fertig! Starte deine neue Shell mit: source .venv/bin/activate")

    except (subprocess.CalledProcessError, Exception) as e:
        print(f"\n💥 FEHLER: {e}")
        _rollback(steps, git_dir, backup_dir)
        sys.exit(1)


def _rollback(steps: list[str], git_dir: Path, backup_dir: Path) -> None:
    """Reverts Git changes to restore the original state."""
    print("🔄 Starte Rollback...")
    if "git_inited" in steps and git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)

    if "git_backup" in steps and backup_dir.exists():
        backup_dir.rename(git_dir)
        print("✅ Ursprünglicher .git-Ordner wurde wiederhergestellt.")
    print("\n❌ Initialisierung fehlgeschlagen. Ursprungszustand wiederhergestellt.")


if __name__ == "__main__":
    init_new_project()
