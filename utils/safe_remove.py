"""
Safe file and directory removal utilities with Windows compatibility.

Provides robust file/folder deletion that handles Windows-specific issues:
- File locking by Explorer or other processes
- Read-only attributes
- Permission errors
- Retry logic with exponential backoff

Author: chamnv-dev
Date: 2025-11-12
"""

import os
import shutil
import stat
import time
from typing import Optional, Callable


def _handle_remove_error(func, path, exc_info):
    """
    Error handler for shutil.rmtree that handles Windows permission issues.
    
    This function is called when shutil.rmtree encounters an error.
    It attempts to fix common Windows issues:
    - Read-only files
    - Permission errors
    - File locking issues
    
    Args:
        func: The function that raised the exception
        path: The path that caused the error
        exc_info: Exception information tuple
    """
    # Check if it's a permission error
    if not os.access(path, os.W_OK):
        # Try to make the file writable
        try:
            os.chmod(path, stat.S_IWUSR | stat.S_IRUSR)
            func(path)
        except Exception:
            pass
    else:
        # If it's not a permission error, try calling the function again
        try:
            func(path)
        except Exception:
            pass


def safe_rmtree(
    path: str,
    max_retries: int = 3,
    retry_delay: float = 0.5,
    log_callback: Optional[Callable] = None
) -> bool:
    """
    Safely remove a directory tree with Windows compatibility.
    
    This function handles Windows-specific issues like file locking and
    read-only attributes. It will retry the operation if it fails due to
    temporary locks.
    
    Args:
        path: Path to the directory to remove
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Delay in seconds between retries (default: 0.5)
        log_callback: Optional callback for logging (default: None)
    
    Returns:
        True if directory was successfully removed, False otherwise
    
    Example:
        >>> safe_rmtree('/tmp/my_temp_dir')
        True
    """
    log = log_callback or (lambda msg: None)
    
    if not os.path.exists(path):
        return True  # Already removed
    
    if not os.path.isdir(path):
        # Not a directory, try to remove as file
        return safe_remove_file(path, max_retries, retry_delay, log_callback)
    
    for attempt in range(max_retries):
        try:
            # Use onerror callback to handle Windows permission issues
            shutil.rmtree(path, onerror=_handle_remove_error)
            
            # Verify removal
            if not os.path.exists(path):
                return True
            
            # If path still exists after rmtree, it might be due to timing
            # Wait a bit and check again
            time.sleep(0.1)
            if not os.path.exists(path):
                return True
                
        except PermissionError as e:
            if attempt < max_retries - 1:
                log(f"[SafeRemove] Permission error on attempt {attempt + 1}/{max_retries}, "
                    f"retrying in {retry_delay}s: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                log(f"[SafeRemove] Failed to remove directory after {max_retries} attempts: {e}")
                return False
                
        except OSError as e:
            # Check if it's a "directory not empty" error on Windows
            if e.winerror == 145 or "directory is not empty" in str(e).lower():
                if attempt < max_retries - 1:
                    log(f"[SafeRemove] Directory not empty, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    log(f"[SafeRemove] Failed to remove directory after {max_retries} attempts: {e}")
                    return False
            else:
                log(f"[SafeRemove] OS error while removing directory: {e}")
                return False
                
        except Exception as e:
            log(f"[SafeRemove] Unexpected error while removing directory: {e}")
            return False
    
    # If we get here, all retries failed
    log(f"[SafeRemove] Failed to remove directory '{path}' after {max_retries} attempts")
    return False


def safe_remove_file(
    path: str,
    max_retries: int = 3,
    retry_delay: float = 0.5,
    log_callback: Optional[Callable] = None
) -> bool:
    """
    Safely remove a file with Windows compatibility.
    
    Handles Windows file locking and read-only attributes.
    
    Args:
        path: Path to the file to remove
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Delay in seconds between retries (default: 0.5)
        log_callback: Optional callback for logging (default: None)
    
    Returns:
        True if file was successfully removed, False otherwise
    
    Example:
        >>> safe_remove_file('/tmp/my_file.txt')
        True
    """
    log = log_callback or (lambda msg: None)
    
    if not os.path.exists(path):
        return True  # Already removed
    
    for attempt in range(max_retries):
        try:
            # Try to make file writable if it's read-only
            if not os.access(path, os.W_OK):
                os.chmod(path, stat.S_IWUSR | stat.S_IRUSR)
            
            os.remove(path)
            
            # Verify removal
            if not os.path.exists(path):
                return True
                
        except PermissionError as e:
            if attempt < max_retries - 1:
                log(f"[SafeRemove] Permission error on attempt {attempt + 1}/{max_retries}, "
                    f"retrying in {retry_delay}s: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                log(f"[SafeRemove] Failed to remove file after {max_retries} attempts: {e}")
                return False
                
        except Exception as e:
            log(f"[SafeRemove] Error while removing file: {e}")
            return False
    
    # If we get here, all retries failed
    log(f"[SafeRemove] Failed to remove file '{path}' after {max_retries} attempts")
    return False


def safe_cleanup_temp_dir(
    temp_dir: str,
    log_callback: Optional[Callable] = None
) -> None:
    """
    Safely cleanup a temporary directory with best-effort approach.
    
    This is a fire-and-forget cleanup that will not raise exceptions.
    Use this for cleanup operations where failure is acceptable.
    
    Args:
        temp_dir: Path to the temporary directory to cleanup
        log_callback: Optional callback for logging (default: None)
    
    Example:
        >>> safe_cleanup_temp_dir('/tmp/my_temp_dir')
    """
    log = log_callback or (lambda msg: None)
    
    try:
        if os.path.exists(temp_dir):
            success = safe_rmtree(temp_dir, max_retries=3, log_callback=log_callback)
            if success:
                log(f"[SafeRemove] Successfully cleaned up temp directory: {temp_dir}")
            else:
                log(f"[SafeRemove] Warning: Could not fully clean up temp directory: {temp_dir}")
    except Exception as e:
        log(f"[SafeRemove] Warning: Unexpected error during temp cleanup: {e}")
