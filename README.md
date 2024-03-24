# python-try

[![Release](https://img.shields.io/github/v/release/vkuehn/python-try)](https://img.shields.io/github/v/release/vkuehn/python-try)
[![Build status](https://img.shields.io/github/actions/workflow/status/vkuehn/python-try/main.yml?branch=main)](https://github.com/vkuehn/python-try/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/vkuehn/python-try/branch/main/graph/badge.svg)](https://codecov.io/gh/vkuehn/python-try)
[![Commit activity](https://img.shields.io/github/commit-activity/m/vkuehn/python-try)](https://img.shields.io/github/commit-activity/m/vkuehn/python-try)
[![License](https://img.shields.io/github/license/vkuehn/python-try)](https://img.shields.io/github/license/vkuehn/python-try)

This is a template repository for Python projects that use Poetry for their dependency management.

- **Github repository**: <https://github.com/vkuehn/python-try/>
- **Documentation** <https://vkuehn.github.io/python-try/>

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:vkuehn/python-try.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
python3 -m venv .venv
source ./venv/bin/activate
pip install -U pip
pip install -r requierments.txt
make install
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPi or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

## Releasing a new version

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
