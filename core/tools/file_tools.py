"""
JCode File Tools - File operations for Agents

Provides file reading, writing, listing capabilities.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    name: str
    size: int
    is_dir: bool
    extension: str


class FileTools:
    """
    File operation tools for Agents.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()

    def read_file(self, file_path: str) -> str:
        """Read file contents."""
        full_path = self._resolve_path(file_path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return full_path.read_text(encoding='utf-8')

    def write_file(self, file_path: str, content: str) -> str:
        """Write content to file."""
        full_path = self._resolve_path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        return str(full_path)

    def list_files(self, directory: str = ".", pattern: str = "*") -> List[FileInfo]:
        """List files in directory."""
        full_path = self._resolve_path(directory)
        if not full_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = []
        for item in full_path.glob(pattern):
            if item.is_dir() and item.name in ['__pycache__', '.git', 'node_modules']:
                continue
            files.append(FileInfo(
                path=str(item.relative_to(self.project_root)),
                name=item.name,
                size=item.stat().st_size if item.is_file() else 0,
                is_dir=item.is_dir(),
                extension=item.suffix
            ))
        return files

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return self._resolve_path(file_path).exists()

    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        full_path = self._resolve_path(file_path)
        if full_path.exists() and full_path.is_file():
            full_path.unlink()
            return True
        return False

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve path relative to project root."""
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.project_root / path


def create_file_tools(project_root: str = ".") -> FileTools:
    """Create FileTools instance."""
    return FileTools(project_root=project_root)


__all__ = ["FileTools", "FileInfo", "create_file_tools"]
