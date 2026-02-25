"""
JCode Git Tools - Git operations for Agents
"""

import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class GitStatus:
    """Git repository status."""
    branch: str
    staged: List[str]
    unstaged: List[str]
    untracked: List[str]
    is_clean: bool


@dataclass
class GitCommit:
    """Git commit info."""
    hash: str
    author: str
    message: str
    date: str


class GitTools:
    """
    Git operation tools for Agents.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()

    def _run_git(self, *args) -> Tuple[int, str, str]:
        """Run git command."""
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def status(self) -> GitStatus:
        """Get git status."""
        _, output, _ = self._run_git("status", "--porcelain")

        staged, unstaged, untracked = [], [], []
        for line in output.split("\n"):
            if not line:
                continue
            status, file = line[:2], line[3:]
            if status[0] != " " and status[0] != "?":
                staged.append(file)
            if status[1] != " ":
                unstaged.append(file)
            if status == "??":
                untracked.append(file)

        _, branch, _ = self._run_git("branch", "--show-current")

        return GitStatus(
            branch=branch or "main",
            staged=staged,
            unstaged=unstaged,
            untracked=untracked,
            is_clean=not (staged or unstaged or untracked)
        )

    def add(self, files: List[str]) -> bool:
        """Stage files."""
        code, _, _ = self._run_git("add", *files)
        return code == 0

    def commit(self, message: str) -> bool:
        """Create commit."""
        code, _, _ = self._run_git("commit", "-m", message)
        return code == 0

    def diff(self, staged: bool = False) -> str:
        """Get diff."""
        args = ["diff"]
        if staged:
            args.append("--staged")
        _, output, _ = self._run_git(*args)
        return output

    def log(self, count: int = 10) -> List[GitCommit]:
        """Get commit log."""
        _, output, _ = self._run_git(
            "log", f"-{count}",
            "--format=%H|%an|%s|%ci"
        )

        commits = []
        for line in output.split("\n"):
            if not line:
                continue
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append(GitCommit(
                    hash=parts[0],
                    author=parts[1],
                    message=parts[2],
                    date=parts[3]
                ))
        return commits

    def is_repo(self) -> bool:
        """Check if directory is a git repo."""
        code, _, _ = self._run_git("status")
        return code == 0


def create_git_tools(project_root: str = ".") -> GitTools:
    """Create GitTools instance."""
    return GitTools(project_root=project_root)


from typing import Tuple
__all__ = ["GitTools", "GitStatus", "GitCommit", "create_git_tools"]
