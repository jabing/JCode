"""
JCode Context Lock - Resource Lock Management

Implements context lock mechanism for managing resource access across JCode agents.
Provides thread-safe locking with timeout/expiration support.

Reference: governance/CONTEXT_LOCK.md
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Lock
from dataclasses import dataclass, field


__all__ = [
    "ContextLock",
    "LockInfo",
    "create_context_lock"
]


@dataclass
class LockInfo:
    """
    Lock information structure.

    Attributes:
        lock_id: Unique lock identifier (UUID)
        owner: Session or agent ID that owns the lock
        resource_paths: List of file/directory paths under lock
        acquired_at: ISO8601 timestamp when lock was acquired
        expires_at: ISO8601 timestamp when lock expires
        timeout_seconds: Original timeout duration in seconds
    """
    lock_id: str
    owner: str
    resource_paths: List[str]
    acquired_at: str
    expires_at: str
    timeout_seconds: int

    def is_expired(self) -> bool:
        """
        Check if the lock has expired.

        Returns:
            True if lock has expired, False otherwise
        """
        try:
            expires_dt = datetime.fromisoformat(self.expires_at)
            return datetime.utcnow() > expires_dt
        except (ValueError, TypeError):
            return True


@dataclass
class ContextLock:
    """
    Context Lock Manager for JCode resource access control.

    Manages in-memory locks with thread-safe operations, timeout support,
    and conflict detection.

    Thread Safety:
        All public methods are thread-safe through internal threading.Lock.
    """

    _locks: Dict[str, LockInfo] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def __post_init__(self):
        """Initialize the context lock manager."""
        self._locks = {}
        self._lock = Lock()

    def acquire(
        self,
        resource_paths: List[str],
        owner: str,
        timeout_seconds: int = 3600
    ) -> str:
        """
        Acquire a lock on specified resources.

        Args:
            resource_paths: List of file/directory paths to lock
            owner: Session or agent ID requesting the lock
            timeout_seconds: Lock duration in seconds (default: 3600)

        Returns:
            Lock ID (UUID string) for tracking

        Raises:
            ValueError: If resource_paths is empty or owner is empty
            RuntimeError: If there's a conflict with existing locks
        """
        if not resource_paths:
            raise ValueError("resource_paths cannot be empty")
        if not owner:
            raise ValueError("owner cannot be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        with self._lock:
            # Check for conflicts with existing locks
            self._cleanup_expired()

            conflicting_locks = self._find_conflicts(resource_paths, owner)
            if conflicting_locks:
                raise RuntimeError(
                    f"Lock conflict: resources locked by {conflicting_locks}"
                )

            # Create new lock
            lock_id = str(uuid.uuid4())
            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=timeout_seconds)

            lock_info = LockInfo(
                lock_id=lock_id,
                owner=owner,
                resource_paths=resource_paths.copy(),
                acquired_at=now.isoformat(),
                expires_at=expires_at.isoformat(),
                timeout_seconds=timeout_seconds
            )

            self._locks[lock_id] = lock_info
            return lock_id

    def release(self, lock_id: str) -> bool:
        """
        Release a lock.

        Args:
            lock_id: Lock ID to release

        Returns:
            True if lock was released, False if lock not found
        """
        if not lock_id:
            return False

        with self._lock:
            if lock_id in self._locks:
                del self._locks[lock_id]
                return True
            return False

    def extend(self, lock_id: str, additional_seconds: int) -> bool:
        """
        Extend a lock's expiration time.

        Args:
            lock_id: Lock ID to extend
            additional_seconds: Additional seconds to extend

        Returns:
            True if lock was extended, False if lock not found or expired

        Raises:
            ValueError: If additional_seconds is not positive
        """
        if additional_seconds <= 0:
            raise ValueError("additional_seconds must be positive")

        with self._lock:
            if lock_id not in self._locks:
                return False

            lock_info = self._locks[lock_id]

            # Check if lock has already expired
            if lock_info.is_expired():
                return False

            # Extend the expiration
            try:
                current_expires = datetime.fromisoformat(lock_info.expires_at)
                new_expires = current_expires + timedelta(seconds=additional_seconds)

                lock_info.expires_at = new_expires.isoformat()
                lock_info.timeout_seconds += additional_seconds
                return True
            except (ValueError, TypeError):
                return False

    def check(self, lock_id: str) -> bool:
        """
        Check if a lock is valid (exists and not expired).

        Args:
            lock_id: Lock ID to check

        Returns:
            True if lock is valid, False otherwise
        """
        if not lock_id:
            return False

        with self._lock:
            if lock_id not in self._locks:
                return False

            return not self._locks[lock_id].is_expired()

    def get_lock_info(self, lock_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a lock.

        Args:
            lock_id: Lock ID to query

        Returns:
            Dictionary with lock information, or None if not found
        """
        if not lock_id:
            return None

        with self._lock:
            if lock_id not in self._locks:
                return None

            lock_info = self._locks[lock_id]
            return {
                "lock_id": lock_info.lock_id,
                "owner": lock_info.owner,
                "resource_paths": lock_info.resource_paths.copy(),
                "acquired_at": lock_info.acquired_at,
                "expires_at": lock_info.expires_at,
                "timeout_seconds": lock_info.timeout_seconds,
                "is_expired": lock_info.is_expired()
            }

    def list_locks(self, owner: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all active locks, optionally filtered by owner.

        Args:
            owner: Optional owner ID to filter by

        Returns:
            List of lock information dictionaries
        """
        with self._lock:
            # Clean up expired locks first
            self._cleanup_expired()

            result = []
            for lock_info in self._locks.values():
                if owner is None or lock_info.owner == owner:
                    result.append({
                        "lock_id": lock_info.lock_id,
                        "owner": lock_info.owner,
                        "resource_paths": lock_info.resource_paths.copy(),
                        "acquired_at": lock_info.acquired_at,
                        "expires_at": lock_info.expires_at,
                        "timeout_seconds": lock_info.timeout_seconds,
                        "is_expired": lock_info.is_expired()
                    })

            return result

    def cleanup_expired(self) -> int:
        """
        Remove all expired locks.

        Returns:
            Number of expired locks removed
        """
        with self._lock:
            return self._cleanup_expired()

    def _cleanup_expired(self) -> int:
        """
        Internal method to remove expired locks (must be called with lock held).

        Returns:
            Number of expired locks removed
        """
        expired_ids = [
            lock_id for lock_id, lock_info in self._locks.items()
            if lock_info.is_expired()
        ]

        for lock_id in expired_ids:
            del self._locks[lock_id]

        return len(expired_ids)

    def _find_conflicts(
        self,
        resource_paths: List[str],
        exclude_owner: str
    ) -> List[str]:
        """
        Find locks that conflict with the requested resource paths.

        Args:
            resource_paths: List of resource paths to check
            exclude_owner: Owner to exclude from conflict check (same owner)

        Returns:
            List of conflicting lock IDs
        """
        conflicts = []

        for lock_id, lock_info in self._locks.items():
            # Skip locks owned by the same owner
            if lock_info.owner == exclude_owner:
                continue

            # Skip expired locks
            if lock_info.is_expired():
                continue

            # Check for any overlap in resource paths
            if any(path in lock_info.resource_paths for path in resource_paths):
                conflicts.append(lock_id)

        return conflicts

    def is_locked(self, resource_path: str) -> bool:
        """
        Check if a specific resource is locked.

        Args:
            resource_path: Resource path to check

        Returns:
            True if resource is locked, False otherwise
        """
        if not resource_path:
            return False

        with self._lock:
            for lock_info in self._locks.values():
                if lock_info.is_expired():
                    continue

                if resource_path in lock_info.resource_paths:
                    return True

            return False

    def get_lock_for_resource(self, resource_path: str) -> Optional[Dict[str, Any]]:
        """
        Get the lock information for a specific resource.

        Args:
            resource_path: Resource path to query

        Returns:
            Lock information dictionary, or None if not locked
        """
        if not resource_path:
            return None

        with self._lock:
            for lock_info in self._locks.values():
                if lock_info.is_expired():
                    continue

                if resource_path in lock_info.resource_paths:
                    return {
                        "lock_id": lock_info.lock_id,
                        "owner": lock_info.owner,
                        "resource_paths": lock_info.resource_paths.copy(),
                        "acquired_at": lock_info.acquired_at,
                        "expires_at": lock_info.expires_at,
                        "timeout_seconds": lock_info.timeout_seconds,
                        "is_expired": lock_info.is_expired()
                    }

            return None

    def __len__(self) -> int:
        """Return the number of active locks."""
        with self._lock:
            self._cleanup_expired()
            return len(self._locks)

    def __repr__(self) -> str:
        """String representation of context lock state."""
        with self._lock:
            return f"ContextLock(active_locks={len(self._locks)})"


def create_context_lock() -> ContextLock:
    """
    Create a ContextLock instance.

    Returns:
        Initialized ContextLock instance
    """
    return ContextLock()
