# utils/video_utils.py
"""
Video Utilities
Provides utilities for video processing including stitching/concatenation
"""

import os
import subprocess
import tempfile
from typing import List, Optional


def stitch_videos(
    video_paths: List[str],
    output_path: str,
    max_duration: float = 30.0,
    log_callback=None
) -> bool:
    """
    Stitch multiple video files into a single video using FFmpeg.
    
    Args:
        video_paths: List of paths to video files to concatenate
        output_path: Path where the stitched video will be saved
        max_duration: Maximum duration of the output video in seconds (default: 30.0)
        log_callback: Optional callback function for logging messages
    
    Returns:
        bool: True if stitching was successful, False otherwise
    
    Raises:
        FileNotFoundError: If any of the input video files don't exist
        RuntimeError: If ffmpeg fails to stitch videos
    """
    log = log_callback or print
    
    # Validate input
    if not video_paths:
        log("[VideoUtils] No videos to stitch")
        return False
    
    if len(video_paths) == 1:
        log("[VideoUtils] Only one video provided, no stitching needed")
        return False
    
    # Check all files exist
    for video_path in video_paths:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
    
    log(f"[VideoUtils] Stitching {len(video_paths)} videos...")
    
    try:
        # Create a temporary file list for ffmpeg concat
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            concat_file = f.name
            for video_path in video_paths:
                # Escape special characters and write absolute path
                abs_path = os.path.abspath(video_path)
                # FFmpeg concat format: file '/path/to/video.mp4'
                f.write(f"file '{abs_path}'\n")
        
        # Build ffmpeg command
        # Using concat demuxer for lossless concatenation
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',  # Copy codec (lossless, fast)
            '-y',  # Overwrite output file
            output_path
        ]
        
        log(f"[VideoUtils] Running FFmpeg concatenation...")
        
        # Run ffmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Clean up temp file
        try:
            os.unlink(concat_file)
        except:
            pass
        
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            log(f"[VideoUtils] FFmpeg error: {error_msg}")
            raise RuntimeError(f"FFmpeg failed to stitch videos: {error_msg}")
        
        # Verify output file exists
        if not os.path.exists(output_path):
            raise RuntimeError("Output file was not created")
        
        # Get duration of output video
        duration = get_video_duration(output_path)
        log(f"[VideoUtils] ✅ Videos stitched successfully! Duration: {duration:.2f}s")
        
        # Check if duration exceeds max_duration
        if duration > max_duration:
            log(f"[VideoUtils] ⚠️ Warning: Output duration ({duration:.2f}s) exceeds maximum ({max_duration:.2f}s)")
            # Note: We don't trim here, just warn. User can adjust scene count.
        
        return True
        
    except subprocess.TimeoutExpired:
        log("[VideoUtils] FFmpeg timeout - videos may be too large")
        raise RuntimeError("Video stitching timed out after 5 minutes")
    except Exception as e:
        log(f"[VideoUtils] Error during video stitching: {str(e)}")
        raise


def get_video_duration(video_path: str) -> float:
    """
    Get the duration of a video file in seconds using FFmpeg.
    
    Args:
        video_path: Path to the video file
    
    Returns:
        float: Duration in seconds
    
    Raises:
        RuntimeError: If ffmpeg fails to get duration
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {result.stderr}")
        
        duration = float(result.stdout.strip())
        return duration
        
    except (ValueError, subprocess.TimeoutExpired) as e:
        raise RuntimeError(f"Failed to get video duration: {str(e)}")


def check_ffmpeg_available() -> bool:
    """
    Check if FFmpeg is available on the system.
    
    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False
