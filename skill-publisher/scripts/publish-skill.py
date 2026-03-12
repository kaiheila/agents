#!/usr/bin/env python3
"""Publish a skill from the current project to the company skills repo."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

DEFAULT_REPO = "git@git.chuanyuapp.com:frontend/skills.git"
DEFAULT_TARGET = "master"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class PublishError(Exception):
    pass


def _project_root() -> str:
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


def _run_git(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise PublishError(result.stderr.strip() or "Git command failed.")
    return result


def _validate_skill(skill_dir: str, name: str) -> None:
    """Validate the skill directory before publishing."""
    if not os.path.isdir(skill_dir):
        raise PublishError(f"Skill directory not found: {skill_dir}")

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise PublishError(f"SKILL.md not found in {skill_dir}")

    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read(4096)
    except OSError as exc:
        raise PublishError(f"Cannot read SKILL.md: {exc}") from exc

    if not content.startswith("---"):
        raise PublishError("SKILL.md missing YAML frontmatter (must start with ---).")

    end = content.find("---", 3)
    if end == -1:
        raise PublishError("SKILL.md frontmatter not closed (missing closing ---).")

    frontmatter = content[3:end]
    if not re.search(r"^name:", frontmatter, re.MULTILINE):
        raise PublishError("SKILL.md frontmatter missing 'name' field.")
    if not re.search(r"^description:", frontmatter, re.MULTILINE):
        raise PublishError("SKILL.md frontmatter missing 'description' field.")

    print(f"  Validated: {name}")


def _clone_repo(repo: str, target: str, tmp_dir: str) -> str:
    repo_dir = os.path.join(tmp_dir, "repo")
    _run_git([
        "git", "clone",
        "--depth", "1",
        "--single-branch",
        "--branch", target,
        repo,
        repo_dir,
    ])
    return repo_dir


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Publish a skill to the company repo.")
    parser.add_argument("name", help="Skill name to publish")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Target Git repo URL")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Target branch for MR")
    parser.add_argument("--src", help="Source skill directory (default: <project>/.agents/skills/<name>)")
    parser.add_argument("--update", action="store_true", help="Allow overwriting existing skill in repo")
    parser.add_argument("--message", "-m", help="Commit message (auto-generated if omitted)")
    args = parser.parse_args(argv)

    name: str = args.name
    if os.sep in name or (os.altsep and os.altsep in name) or name in (".", ".."):
        print(f"Error: Invalid skill name '{name}'.", file=sys.stderr)
        return 1

    if args.src:
        skill_src = args.src
    else:
        skill_src = os.path.join(_project_root(), ".agents", "skills", name)

    print(f"Publishing '{name}' from {skill_src}...")

    try:
        _validate_skill(skill_src, name)

        tmp_dir = tempfile.mkdtemp(prefix="skill-publish-")
        try:
            print(f"  Cloning {args.repo}...")
            repo_dir = _clone_repo(args.repo, args.target, tmp_dir)

            dest_dir = os.path.join(repo_dir, name)
            if os.path.exists(dest_dir):
                if not args.update:
                    raise PublishError(
                        f"Skill '{name}' already exists in repo. "
                        f"Use --update to overwrite."
                    )
                shutil.rmtree(dest_dir)
                print(f"  Updating existing skill '{name}'...")
            else:
                print(f"  Adding new skill '{name}'...")

            shutil.copytree(skill_src, dest_dir)

            branch = f"publish/{name}"
            try:
                _run_git(["git", "-C", repo_dir, "checkout", "-b", branch])
            except PublishError:
                branch = f"publish/{name}-{os.getpid()}"
                _run_git(["git", "-C", repo_dir, "checkout", "-b", branch])

            _run_git(["git", "-C", repo_dir, "add", name])

            action = "Update" if args.update else "Add"
            commit_msg = args.message or f"{action} skill: {name}"
            _run_git(["git", "-C", repo_dir, "commit", "-m", commit_msg])

            print(f"  Pushing branch '{branch}'...")
            _run_git([
                "git", "-C", repo_dir, "push",
                "-o", "merge_request.create",
                "-o", f"merge_request.target={args.target}",
                "-o", f"merge_request.title={action} skill: {name}",
                "-u", "origin", branch,
            ])

            print(f"\nDone! Skill '{name}' published on branch '{branch}'.")
            print(f"A Merge Request has been created targeting '{args.target}'.")

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        return 0

    except PublishError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
