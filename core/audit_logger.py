"""
JCode Audit Logger - Unified Audit Log System

Implements the unified audit log format for JCode Agent System v3.0 and
OpenCode Superpowers Integration.

Reference: governance/AUDIT_LOG_SPEC.md
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

__all__ = [
    "AuditLogger",
    "create_audit_logger",
    "calculate_details_hash",
    "verify_log_integrity",
]


class AuditLogger:
    """
    JCode Unified Audit Logger

    Writes and queries audit logs in JSONL (JSON Lines) format.
    Supports agent executions, human interventions, quick fixes, and
    OpenCode MCP server interactions.
    """

    def __init__(self, log_dir: str = ".jcode/audit"):
        """
        Initialize audit logger.

        Args:
            log_dir: Directory to store audit logs (default: .jcode/audit)
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / "audit.log"

        # Create directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def write_log(
        self,
        actor_type: str,
        actor_id: str,
        action_type: str,
        context: Dict[str, Any],
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Write a log entry to the audit log.

        Args:
            actor_type: Type of actor (analyst|planner|implementer|reviewer|tester|conductor|human|system|mcp_server)
            actor_id: Identifier for the actor (session_id or user_id)
            action_type: Type of action (ANALYSIS|TASKS|IMPLEMENTATION|REVIEW|TEST|FINAL|HUMAN_INTERVENTION|MCP_SERVER_CALL|etc)
            context: Contextual information (task_id, iteration, stage, session_id)
            details: Action-specific details (optional, defaults to empty dict)

        Returns:
            log_id of the created entry
        """
        if details is None:
            details = {}

        # Generate log ID and timestamp
        log_id = f"JCODE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}-{uuid.uuid4().hex[:6]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Calculate content hash for integrity
        content_hash = calculate_details_hash(details)

        # Build log entry
        log_entry = {
            "log_id": log_id,
            "timestamp": timestamp,
            "actor_type": actor_type.upper(),
            "actor_id": actor_id,
            "action_type": action_type.upper(),
            "context": context,
            "details": details,
            "integrity": {
                "content_hash": content_hash,
            },
            "metadata": {
                "source_system": "JCODE",
                "log_version": "1.0",
            },
        }

        # Write to log file (append mode, one JSON object per line)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        return log_id

    def query_logs(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query logs with optional filters.

        Args:
            filters: Dictionary of field filters (e.g., {"actor_type": "AGENT", "action_type": "ANALYSIS_COMPLETE"})
            limit: Maximum number of results to return (default: 100)

        Returns:
            List of matching log entries, most recent first
        """
        if not self.log_file.exists():
            return []

        results = []

        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)

                    # Apply filters
                    if filters:
                        match = True
                        for key, value in filters.items():
                            if key not in entry:
                                match = False
                                break
                            if entry[key] != value:
                                match = False
                                break
                        if not match:
                            continue

                    results.append(entry)

                except json.JSONDecodeError:
                    # Skip invalid lines
                    continue

        # Sort by timestamp (most recent first) and apply limit
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results[:limit]

    def get_session_log(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all logs for a specific session.

        Args:
            session_id: Session identifier to filter by

        Returns:
            List of log entries for the session, chronologically ordered
        """
        logs = self.query_logs(filters={"actor_id": session_id}, limit=10000)
        logs.sort(key=lambda x: x["timestamp"])
        return logs

    def clear_logs(self) -> None:
        """
        Clear all logs (for testing purposes only).

        WARNING: This is a destructive operation. Use with caution.
        """
        if self.log_file.exists():
            self.log_file.unlink()


def create_audit_logger(log_dir: Optional[str] = None) -> AuditLogger:
    """
    Factory function to create an AuditLogger instance.

    Args:
        log_dir: Directory to store audit logs (defaults to .jcode/audit)

    Returns:
        Initialized AuditLogger instance
    """
    if log_dir is None:
        log_dir = ".jcode/audit"

    return AuditLogger(log_dir=log_dir)


def calculate_details_hash(details: Dict[str, Any]) -> str:
    """
    Calculate SHA-256 hash of details field for integrity verification.

    Args:
        details: Details dictionary to hash

    Returns:
        Hexadecimal SHA-256 hash string
    """
    # Canonicalize JSON: sorted keys, no extra whitespace
    details_json = json.dumps(details, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(details_json.encode()).hexdigest()


def verify_log_integrity(entry: Dict[str, Any]) -> bool:
    """
    Verify log entry integrity by checking hash.

    Args:
        entry: Log entry to verify

    Returns:
        True if entry is valid (hash matches), False otherwise
    """
    if "integrity" not in entry or "details" not in entry:
        return False

    calculated_hash = calculate_details_hash(entry["details"])
    stored_hash = entry["integrity"].get("content_hash")

    return calculated_hash == stored_hash
