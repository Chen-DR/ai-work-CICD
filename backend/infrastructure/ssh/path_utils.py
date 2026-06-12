import os


def normalize_remote_path(path: str) -> str:
    """Normalize a remote path, preventing path traversal."""
    return os.path.normpath(path)


def is_subpath(child: str, parent: str) -> bool:
    """Check if child path is within parent path."""
    child_norm = os.path.abspath(child)
    parent_norm = os.path.abspath(parent)
    return child_norm.startswith(parent_norm + "/") or child_norm == parent_norm
