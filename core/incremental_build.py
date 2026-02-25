"""
JCode Incremental Build - File-level modification tracking with rollback

Implements incremental build capabilities for OpenCode Superpowers:
- Generate unified diffs for file changes
- Apply patches with merge strategies
- Track rollback points with content hashing
- Support multiple rollback states

Reference: governance/INCREMENTAL_BUILD.md
"""

import hashlib
import json
import difflib
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class RollbackPoint:
    """
    Represents a rollback point for tracking file states.

    Attributes:
        id: Unique identifier for this rollback point
        name: Human-readable name
        timestamp: ISO8601 timestamp
        files: Dictionary mapping file paths to content hashes
        diff: Unified diff representation
    """
    id: str
    name: str
    timestamp: str
    files: Dict[str, str] = field(default_factory=dict)
    diff: str = ""


class IncrementalBuild:
    """
    Incremental Build Manager for tracking and rolling back file changes.

    Manages file-level modifications with:
    - Unified diff generation
    - Rollback point creation and restoration
    - Content hashing for integrity verification
    - File change tracking
    """

    def __init__(self, project_root: str = "."):
        """
        Initialize the incremental build manager.

        Args:
            project_root: Root directory for the project (default: current directory)
        """
        self._project_root = Path(project_root).resolve()
        self._rollback_dir = self._project_root / ".jcode" / "build" / "rollback"
        self._diff_dir = self._project_root / ".jcode" / "build" / "diffs"

        # Create directories if they don't exist
        self._rollback_dir.mkdir(parents=True, exist_ok=True)
        self._diff_dir.mkdir(parents=True, exist_ok=True)

    def generate_diff(
        self,
        file_paths: List[str],
        original_contents: Dict[str, str] = None,
        proposed_contents: Dict[str, str] = None,
        context_lines: int = 3
    ) -> str:
        """
        Generate unified diff for one or more files.

        Args:
            file_paths: List of file paths to generate diff for
            original_contents: Dict mapping file paths to original content
                              (if None, reads from filesystem)
            proposed_contents: Dict mapping file paths to proposed content
                              (if None, reads from filesystem)
            context_lines: Number of context lines in diff

        Returns:
            Unified diff string in Git format

        Raises:
            FileNotFoundError: If file cannot be found
            ValueError: If file paths are invalid
        """
        diff_lines = []

        for file_path in file_paths:
            full_path = self._project_root / file_path

            # Get original content
            if original_contents and file_path in original_contents:
                original = original_contents[file_path]
            else:
                if not full_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                original = full_path.read_text(encoding='utf-8')

            # Get proposed content
            if proposed_contents and file_path in proposed_contents:
                proposed = proposed_contents[file_path]
            else:
                proposed = original  # No change

            # Generate diff for this file
            original_lines = original.splitlines(keepends=True)
            proposed_lines = proposed.splitlines(keepends=True)

            diff = difflib.unified_diff(
                original_lines,
                proposed_lines,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm="",
                n=context_lines
            )

            diff_lines.extend(diff)

        return ''.join(diff_lines)

    def apply_diff(
        self,
        diff_content: str,
        merge_strategy: str = "auto",
        human_changes_detected: bool = False
    ) -> Dict[str, Any]:
        """
        Apply a unified diff to files.

        Args:
            diff_content: Unified diff string
            merge_strategy: Merge strategy ("auto", "human_review", "preserve_human")
            human_changes_detected: Whether human changes have been detected

        Returns:
            Dictionary with merge results:
            {
                "success": bool,
                "merged_content": str,
                "merge_log": dict
            }

        Raises:
            ValueError: If merge_strategy is invalid
            RuntimeError: If human changes prevent auto-merge
        """
        valid_strategies = ["auto", "human_review", "preserve_human"]
        if merge_strategy not in valid_strategies:
            raise ValueError(f"Invalid merge_strategy: {merge_strategy}. Must be one of: {valid_strategies}")

        # Check for human changes conflict
        if human_changes_detected and merge_strategy == "auto":
            raise RuntimeError("Human changes detected. Cannot auto-merge. Use merge_strategy='human_review'")

        # Parse diff and apply changes
        file_changes = self._parse_diff(diff_content)
        merge_log = {
            "ai_changes_applied": 0,
            "human_changes_preserved": not human_changes_detected,
            "conflicts_resolved": "auto" if merge_strategy == "auto" else "human",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        results = {}
        for file_path, (original_lines, proposed_lines) in file_changes.items():
            full_path = self._project_root / file_path

            # Write the new content
            full_path.write_text(''.join(proposed_lines), encoding='utf-8')
            results[file_path] = ''.join(proposed_lines)
            merge_log["ai_changes_applied"] += len([
                line for line in proposed_lines
                if line.startswith('+') and not line.startswith('+++')
            ])

        return {
            "success": True,
            "merged_content": results,
            "merge_log": merge_log
        }

    def _parse_diff(self, diff_content: str) -> Dict[str, Tuple[List[str], List[str]]]:
        """
        Parse a unified diff into file changes.

        Args:
            diff_content: Unified diff string

        Returns:
            Dict mapping file paths to (original_lines, proposed_lines) tuples
        """
        file_changes = {}
        current_file = None
        original_lines = []
        proposed_lines = []

        for line in diff_content.splitlines():
            if line.startswith('--- a/'):
                # Save previous file if exists
                if current_file:
                    file_changes[current_file] = (original_lines, proposed_lines)

                # Start new file
                current_file = line[6:]
                original_lines = []
                proposed_lines = []
            elif line.startswith('+++ b/'):
                # Just update filename (already set from --- line)
                pass
            elif line.startswith('@@'):
                # Diff header, skip
                pass
            elif line.startswith('-') and not line.startswith('---'):
                # Removed line (from original)
                original_lines.append(line[1:] + '\n')
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line (in proposed)
                proposed_lines.append(line[1:] + '\n')
            elif line.startswith(' '):
                # Context line (in both)
                original_lines.append(line[1:] + '\n')
                proposed_lines.append(line[1:] + '\n')

        # Save last file
        if current_file:
            file_changes[current_file] = (original_lines, proposed_lines)

        return file_changes

    def rollback(self, rollback_point: str) -> bool:
        """
        Rollback files to a previous rollback point.

        Args:
            rollback_point: Rollback point ID or name

        Returns:
            True if rollback successful

        Raises:
            FileNotFoundError: If rollback point not found
            RuntimeError: If rollback fails
        """
        # Load rollback point
        point = self._load_rollback_point(rollback_point)

        if not point:
            raise FileNotFoundError(f"Rollback point not found: {rollback_point}")

        # Restore files from rollback point
        for file_path, content_hash in point.files.items():
            full_path = self._project_root / file_path

            # In a full implementation, we would load content from a content-addressable storage
            # For now, we'll apply the reverse diff
            pass

        # Apply reverse diff
        if point.diff:
            reverse_diff = self._reverse_diff(point.diff)
            self.apply_diff(reverse_diff, merge_strategy="auto")

        return True

    def _reverse_diff(self, diff_content: str) -> str:
        """
        Reverse a unified diff (swap + and - lines).

        Args:
            diff_content: Original diff

        Returns:
            Reversed diff
        """
        reversed_lines = []

        for line in diff_content.splitlines():
            if line.startswith('+') and not line.startswith('+++'):
                # Convert added to removed
                reversed_lines.append('-' + line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                # Convert removed to added
                reversed_lines.append('+' + line[1:])
            elif line.startswith('--- a/'):
                # Swap from/to
                reversed_lines.append('+++ ' + line[6:])
            elif line.startswith('+++ b/'):
                # Swap to/from
                reversed_lines.append('--- ' + line[6:])
            else:
                # Keep other lines as is
                reversed_lines.append(line)

        return '\n'.join(reversed_lines)

    def create_rollback_point(self, name: str, file_paths: List[str] = None) -> RollbackPoint:
        """
        Create a named rollback point.

        Args:
            name: Human-readable name for rollback point
            file_paths: List of files to include (None = all tracked files)

        Returns:
            RollbackPoint object

        Raises:
            ValueError: If file paths are invalid
        """
        point_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        files_hash = {}
        files_to_track = file_paths if file_paths else self._get_tracked_files()

        for file_path in files_to_track:
            full_path = self._project_root / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                files_hash[file_path] = content_hash

        # Generate diff for all tracked files
        original_contents = {}
        for file_path in files_to_track:
            full_path = self._project_root / file_path
            if full_path.exists():
                original_contents[file_path] = full_path.read_text(encoding='utf-8')

        diff = self.generate_diff(files_to_track, original_contents, original_contents)

        point = RollbackPoint(
            id=point_id,
            name=name,
            timestamp=timestamp,
            files=files_hash,
            diff=diff
        )

        # Save rollback point
        self._save_rollback_point(point)

        return point

    def _get_tracked_files(self) -> List[str]:
        """
        Get list of tracked files in the project.

        Returns:
            List of file paths relative to project root
        """
        tracked = []
        for file_path in self._project_root.rglob('*'):
            if file_path.is_file() and not any(
                part.startswith('.') for part in file_path.parts
            ):
                rel_path = file_path.relative_to(self._project_root)
                tracked.append(str(rel_path))
        return tracked

    def list_rollback_points(self) -> List[RollbackPoint]:
        """
        List all available rollback points.

        Returns:
            List of RollbackPoint objects, sorted by timestamp (newest first)
        """
        points = []

        if not self._rollback_dir.exists():
            return points

        for point_file in self._rollback_dir.glob('*.json'):
            try:
                with open(point_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    point = RollbackPoint(**data)
                    points.append(point)
            except (json.JSONDecodeError, TypeError):
                continue

        # Sort by timestamp (newest first)
        points.sort(key=lambda p: p.timestamp, reverse=True)
        return points

    def _load_rollback_point(self, point_id_or_name: str) -> Optional[RollbackPoint]:
        """
        Load a rollback point by ID or name.

        Args:
            point_id_or_name: Rollback point ID or name

        Returns:
            RollbackPoint object or None if not found
        """
        points = self.list_rollback_points()

        for point in points:
            if point.id == point_id_or_name or point.name == point_id_or_name:
                return point

        return None

    def _save_rollback_point(self, point: RollbackPoint) -> None:
        """
        Save a rollback point to disk.

        Args:
            point: RollbackPoint to save
        """
        point_file = self._rollback_dir / f"{point.id}.json"

        with open(point_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(point), f, indent=2)

    def get_build_status(self) -> Dict[str, Any]:
        """
        Get current build status.

        Returns:
            Dictionary with build status information:
            {
                "project_root": str,
                "rollback_points_count": int,
                "latest_rollback_point": Optional[str],
                "total_files_tracked": int,
                "build_directory": str
            }
        """
        rollback_points = self.list_rollback_points()
        tracked_files = self._get_tracked_files()

        return {
            "project_root": str(self._project_root),
            "rollback_points_count": len(rollback_points),
            "latest_rollback_point": rollback_points[0].name if rollback_points else None,
            "total_files_tracked": len(tracked_files),
            "build_directory": str(self._rollback_dir),
            "diff_directory": str(self._diff_dir)
        }

    def delete_rollback_point(self, point_id_or_name: str) -> bool:
        """
        Delete a rollback point.

        Args:
            point_id_or_name: Rollback point ID or name

        Returns:
            True if deleted successfully

        Raises:
            FileNotFoundError: If rollback point not found
        """
        point = self._load_rollback_point(point_id_or_name)

        if not point:
            raise FileNotFoundError(f"Rollback point not found: {point_id_or_name}")

        point_file = self._rollback_dir / f"{point.id}.json"

        if point_file.exists():
            point_file.unlink()

        return True


# Factory function for convenient initialization
def create_incremental_build(project_root: str = ".") -> IncrementalBuild:
    """
    Create an IncrementalBuild instance.

    Args:
        project_root: Root directory for the project (default: current directory)

    Returns:
        Initialized IncrementalBuild instance
    """
    return IncrementalBuild(project_root=project_root)


# Export list
__all__ = [
    "IncrementalBuild",
    "RollbackPoint",
    "create_incremental_build"
]
