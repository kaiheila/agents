#!/usr/bin/env python3
"""List skills from the company Git repo."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

DEFAULT_REPO = "git@git.chuanyuapp.com:frontend/skills.git"
DEFAULT_REF = "master"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class ListError(Exception):
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


def _installed_skills() -> dict[str, str]:
    """Return {name: path} of locally installed skills."""
    root = _skills_home()
    result: dict[str, str] = {}
    if not os.path.isdir(root):
        return result
    for name in os.listdir(root):
        skill_dir = os.path.join(root, name)
        if os.path.isdir(skill_dir) and os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
            result[name] = skill_dir
    return result


def _parse_frontmatter(skill_md_path: str) -> dict[str, str]:
    """Extract name and description from SKILL.md YAML frontmatter."""
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read(4096)
    except OSError:
        return {}

    if not content.startswith("---"):
        return {}

    end = content.find("---", 3)
    if end == -1:
        return {}

    frontmatter = content[3:end]
    result: dict[str, str] = {}

    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        result["name"] = name_match.group(1).strip().strip("\"'")

    desc_match = re.search(r"^description:\s*(.+?)(?=\n\w|\n---|\Z)", frontmatter, re.MULTILINE | re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip().strip("\"'")
        desc = re.sub(r"\s+", " ", desc)
        result["description"] = desc

    return result


def _clone_repo(repo: str, ref: str) -> str:
    """Shallow clone the repo to a temp directory, return the path."""
    tmp_dir = tempfile.mkdtemp(prefix="skill-list-")
    cmd = [
        "git", "clone",
        "--depth", "1",
        "--single-branch",
        "--branch", ref,
        repo,
        tmp_dir,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise ListError(f"Failed to clone repo: {result.stderr.strip()}")
    return tmp_dir


def _discover_skills(repo_dir: str) -> list[dict[str, str]]:
    """Find all skill directories (containing SKILL.md) in the repo root."""
    skills: list[dict[str, str]] = []
    for entry in sorted(os.listdir(repo_dir)):
        if entry.startswith("."):
            continue
        skill_dir = os.path.join(repo_dir, entry)
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if os.path.isdir(skill_dir) and os.path.isfile(skill_md):
            meta = _parse_frontmatter(skill_md)
            skills.append({
                "name": meta.get("name", entry),
                "dir_name": entry,
                "description": meta.get("description", ""),
            })
    return skills


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="List skills from company repo.")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Git repo URL")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Branch or tag")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--installed-only", action="store_true", help="Only show installed skills")
    args = parser.parse_args(argv)

    installed = _installed_skills()

    if args.installed_only:
        if args.format == "json":
            payload = [{"name": name, "path": path} for name, path in sorted(installed.items())]
            print(json.dumps(payload, ensure_ascii=False))
        else:
            if not installed:
                print("No skills installed.")
            else:
                for idx, (name, path) in enumerate(sorted(installed.items()), 1):
                    print(f"  {idx}. {name} ({path})")
        return 0

    try:
        repo_dir = _clone_repo(args.repo, args.ref)
    except ListError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        skills = _discover_skills(repo_dir)
    finally:
        shutil.rmtree(repo_dir, ignore_errors=True)

    if args.format == "json":
        payload = [
            {
                "name": s["name"],
                "dir_name": s["dir_name"],
                "description": s["description"],
                "installed": s["dir_name"] in installed or s["name"] in installed,
            }
            for s in skills
        ]
        print(json.dumps(payload, ensure_ascii=False))
    else:
        if not skills:
            print("No skills found in repo.")
        else:
            for idx, s in enumerate(skills, 1):
                is_installed = s["dir_name"] in installed or s["name"] in installed
                tag = " (已安装)" if is_installed else ""
                raw_desc = s["description"]
                desc = f" - {raw_desc[:80]}..." if len(raw_desc) > 80 else f" - {raw_desc}" if raw_desc else ""
                print(f"  {idx}. {s['dir_name']}{desc}{tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
