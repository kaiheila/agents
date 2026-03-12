#!/usr/bin/env python3
"""Install skills from the company Git repo."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

DEFAULT_REPO = "git@git.chuanyuapp.com:frontend/skills.git"
DEFAULT_REF = "master"


class InstallError(Exception):
    pass


def _project_root() -> str:
    """Find the project root via git, fall back to cwd."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return os.getcwd()


def _skills_home() -> str:
    """Project-level skills directory. Never use system-level paths."""
    if os.environ.get("SKILLS_HOME"):
        return os.environ["SKILLS_HOME"]
    return os.path.join(_project_root(), ".agents", "skills")


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise InstallError(result.stderr.strip() or "Git command failed.")
    return result


def _sparse_clone(repo: str, ref: str, paths: list[str], dest_dir: str) -> str:
    """Sparse checkout only the requested skill directories."""
    repo_dir = os.path.join(dest_dir, "repo")
    _run_git([
        "git", "clone",
        "--filter=blob:none",
        "--depth", "1",
        "--sparse",
        "--single-branch",
        "--branch", ref,
        repo,
        repo_dir,
    ])
    _run_git(["git", "-C", repo_dir, "sparse-checkout", "set", *paths])
    return repo_dir


def _validate_skill(skill_dir: str, name: str) -> None:
    if not os.path.isdir(skill_dir):
        raise InstallError(f"Skill '{name}' not found in repo.")
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise InstallError(f"Skill '{name}' has no SKILL.md.")


def _copy_skill(src: str, dest: str, name: str) -> None:
    if os.path.exists(dest):
        raise InstallError(
            f"'{name}' already installed at {dest}. "
            f"To reinstall, first delete the directory."
        )
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copytree(src, dest)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Install skills from company repo.")
    parser.add_argument("names", nargs="+", help="Skill name(s) to install")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Git repo URL")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Branch or tag")
    parser.add_argument("--dest", help="Destination directory (default: <project>/.agents/skills/)")
    args = parser.parse_args(argv)

    dest_root = args.dest or _skills_home()
    names: list[str] = args.names

    for name in names:
        if os.sep in name or (os.altsep and os.altsep in name) or name in (".", ".."):
            print(f"Error: Invalid skill name '{name}'.", file=sys.stderr)
            return 1

    tmp_dir = tempfile.mkdtemp(prefix="skill-install-")
    try:
        print(f"Fetching skills from {args.repo} ({args.ref})...")
        repo_dir = _sparse_clone(args.repo, args.ref, names, tmp_dir)

        installed: list[tuple[str, str]] = []
        for name in names:
            skill_src = os.path.join(repo_dir, name)
            _validate_skill(skill_src, name)
            skill_dest = os.path.join(dest_root, name)
            _copy_skill(skill_src, skill_dest, name)
            installed.append((name, skill_dest))

        for name, dest in installed:
            print(f"Installed: {name} -> {dest}")

        return 0

    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
