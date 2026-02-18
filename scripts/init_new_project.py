"""Initialize a new project from this template.

This script removes the existing `.git` history and initializes a fresh git
repository. Optionally, it can attach a new `origin` remote.
"""

import argparse
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
    project_root : Path
        The root directory of the project.
    """
    pyproject_file = project_root / "pyproject.toml"
    pyproject_data = tomlkit.loads(pyproject_file.read_text())

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

    # Update tool configs for new package name
    pyproject_data["tool"]["mypy"]["files"] = [f"src/{config.name}"]
    pyproject_data["tool"]["coverage"]["run"]["source"] = [f"src/{config.name}"]

    # Write the updated data back to the pyproject.toml file
    pyproject_file.write_text(tomlkit.dumps(pyproject_data))


def _rename_package_directory(old_name: str, new_name: str, project_root: Path) -> None:
    """Rename the package directory from old_name to new_name.

    Parameters
    ----------
    old_name : str
        The current package name.
    new_name : str
        The new package name.
    project_root : Path
        The root directory of the project.
    """
    old_path = project_root / "src" / old_name
    new_path = project_root / "src" / new_name

    if old_path.exists():
        old_path.rename(new_path)
        print(f"📦 Renamed package: src/{old_name} -> src/{new_name}")


def _update_devcontainer(old_name: str, new_name: str, project_root: Path) -> None:
    """Update project name references in devcontainer.json.

    Parameters
    ----------
    old_name : str
        The old project name to replace.
    new_name : str
        The new project name.
    project_root : Path
        The root directory of the project.
    """
    devcontainer_file = project_root / ".devcontainer" / "devcontainer.json"
    if not devcontainer_file.exists():
        return

    content = devcontainer_file.read_text()
    content = content.replace(f'"name": "{old_name}"', f'"name": "{new_name}"')
    content = content.replace(f"/workspaces/{old_name}", f"/workspaces/{new_name}")
    devcontainer_file.write_text(content)
    print(f"🐳 Updated devcontainer.json: {old_name} -> {new_name}")


def _update_readme(old_name_dash: str, new_name_dash: str, project_root: Path) -> None:
    """Update project name references in README.md.

    Parameters
    ----------
    old_name_dash : str
        The old project name with dashes (e.g., python-try).
    new_name_dash : str
        The new project name with dashes.
    project_root : Path
        The root directory of the project.
    """
    readme_file = project_root / "README.md"
    if not readme_file.exists():
        return

    content = readme_file.read_text()
    content = content.replace(f"# {old_name_dash}", f"# {new_name_dash}")
    content = content.replace("python-try/", f"{new_name_dash}/")
    content = content.replace(old_name_dash, new_name_dash)

    readme_file.write_text(content)
    print("📖 Updated README.md")


def _update_mkdocs_yml(old_name_dash: str, new_name_dash: str, project_root: Path) -> None:
    """Update site name and URLs in mkdocs.yml.

    Parameters
    ----------
    old_name_dash : str
        The old project name with dashes.
    new_name_dash : str
        The new project name with dashes.
    project_root : Path
        The root directory of the project.
    """
    mkdocs_file = project_root / "mkdocs.yml"
    if not mkdocs_file.exists():
        return

    content = mkdocs_file.read_text()
    content = content.replace(f"site_name: {old_name_dash}", f"site_name: {new_name_dash}")
    content = content.replace("/python-try", f"/{new_name_dash}")
    content = content.replace(f"/{old_name_dash}", f"/{new_name_dash}")

    mkdocs_file.write_text(content)
    print("🌐 Updated mkdocs.yml")


def _update_dockerfile(old_name: str, new_name: str, project_root: Path) -> None:
    """Update package import in Dockerfile.

    Parameters
    ----------
    old_name : str
        The old package name with underscores.
    new_name : str
        The new package name with underscores.
    project_root : Path
        The root directory of the project.
    """
    dockerfile = project_root / "Dockerfile"
    if not dockerfile.exists():
        return

    content = dockerfile.read_text()
    content = content.replace(f"from {old_name}.main", f"from {new_name}.main")

    dockerfile.write_text(content)
    print("🐳 Updated Dockerfile")


def _update_docker_compose(old_name_dash: str, new_name_dash: str, project_root: Path) -> None:
    """Update project name references in docker-compose.yml.

    Parameters
    ----------
    old_name_dash : str
        The old project name with dashes.
    new_name_dash : str
        The new project name with dashes.
    project_root : Path
        The root directory of the project.
    """
    docker_compose_file = project_root / "docker-compose.yml"
    if not docker_compose_file.exists():
        return

    content = docker_compose_file.read_text()
    content = content.replace(f"image: {old_name_dash}:latest", f"image: {new_name_dash}:latest")
    content = content.replace(f"container_name: {old_name_dash}-app", f"container_name: {new_name_dash}-app")
    content = content.replace(f"container_name: {old_name_dash}-dev", f"container_name: {new_name_dash}-dev")
    content = content.replace(f"/workspaces/{old_name_dash}", f"/workspaces/{new_name_dash}")
    content = content.replace(f"{old_name_dash}-venv", f"{new_name_dash}-venv")
    content = content.replace(f"{old_name_dash}-uv-cache", f"{new_name_dash}-uv-cache")

    docker_compose_file.write_text(content)
    print("🐳 Updated docker-compose.yml")


def _update_makefile(old_name_dash: str, new_name_dash: str, project_root: Path) -> None:
    """Update Docker image tag in Makefile.

    Parameters
    ----------
    old_name_dash : str
        The old project name with dashes.
    new_name_dash : str
        The new project name with dashes.
    project_root : Path
        The root directory of the project.
    """
    makefile = project_root / "Makefile"
    if not makefile.exists():
        return

    content = makefile.read_text()
    content = content.replace(f"-t {old_name_dash}", f"-t {new_name_dash}")

    makefile.write_text(content)
    print("🏗️  Updated Makefile")


def _update_tox_ini(old_name: str, new_name: str, project_root: Path) -> None:
    """Update package paths in tox.ini.

    Parameters
    ----------
    old_name : str
        The old package name with underscores.
    new_name : str
        The new package name with underscores.
    project_root : Path
        The root directory of the project.
    """
    tox_file = project_root / "tox.ini"
    if not tox_file.exists():
        return

    content = tox_file.read_text()
    content = content.replace(f"src/{old_name}", f"src/{new_name}")
    content = content.replace(f"./{old_name}", f"./{new_name}")

    tox_file.write_text(content)
    print("⚙️  Updated tox.ini")


def _get_user_input(user_email: str, user_name: str, project_name: str | None = None) -> ProjectConfig:
    """Gather project configuration from user input or arguments.

    Parameters
    ----------
    user_email : str
        Default email from git config.
    user_name : str
        Default author name from git config.
    project_name : str | None
        Optional project name from command-line arguments.

    Returns:
    -------
    ProjectConfig
        Complete project configuration.
    """
    if project_name:
        name = project_name
        print(f"📝 Using project name: {name}")
    else:
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


def init_new_project(project_name: str | None = None) -> None:
    """Remove the existing git history and initialize a fresh repository.

    Parameters
    ----------
    project_name : str | None
        Optional project name from command-line arguments.
    """
    project_root = Path(__file__).parent.parent
    git_dir = project_root / ".git"

    git = _resolve_executable("git")

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
    config = _get_user_input(user_email=user_email, user_name=user_name, project_name=project_name)

    # 1. Remove old git history
    if git_dir.exists():
        print(f"🔥 Removing old git history at {git_dir}...")
        shutil.rmtree(git_dir, ignore_errors=True)

    # 2. Initialize new git repo
    print("🌱 Initializing new git repository...")
    subprocess.run([git, "init", "-b", "main"], cwd=project_root, check=True)  # noqa: S603

    # 3. Ask for new remote
    new_remote = config.repository_url

    if new_remote:
        subprocess.run([git, "remote", "add", "origin", new_remote], cwd=project_root, check=True)  # noqa: S603
        print(f"✅ Remote 'origin' set to: {new_remote}")
    else:
        print("INFO: Skipping remote setup. You can add it later with 'git remote add origin <url>'")

    # 4. Rename package directory
    _rename_package_directory(old_name="python_try", new_name=config.name, project_root=project_root)

    # 5. Update pyproject.toml with new project metadata
    print("📝 Updating pyproject.toml with new project metadata...")
    _update_pyproject_toml(config=config, project_root=project_root)

    # 6. Update all template references to old project names
    old_name_dash = "python-try"
    new_name_dash = config.name.replace("_", "-")

    _update_devcontainer(old_name="python-try", new_name=new_name_dash, project_root=project_root)
    _update_readme(old_name_dash=old_name_dash, new_name_dash=new_name_dash, project_root=project_root)
    _update_mkdocs_yml(old_name_dash=old_name_dash, new_name_dash=new_name_dash, project_root=project_root)
    _update_dockerfile(old_name="python_try", new_name=config.name, project_root=project_root)
    _update_docker_compose(old_name_dash=old_name_dash, new_name_dash=new_name_dash, project_root=project_root)
    _update_makefile(old_name_dash=old_name_dash, new_name_dash=new_name_dash, project_root=project_root)
    _update_tox_ini(old_name="python_try", new_name=config.name, project_root=project_root)

    # 7. Initial commit with all updated configs
    print("📦 Creating initial commit...")
    subprocess.run([git, "add", "."], cwd=project_root, check=True)  # noqa: S603
    subprocess.run(  # noqa: S603
        [git, "commit", "-m", f"Initial commit from {config.name} template"],
        cwd=project_root,
        check=True,
    )

    print("\n✨ You can now push to your new origin.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a new project from the python-try template.")
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        help="Project name (if not provided, will prompt interactively)",
    )
    args = parser.parse_args()
    init_new_project(project_name=args.name)
