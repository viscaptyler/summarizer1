import os
import mimetypes
from datetime import timedelta

def format_time(seconds):
    """
    Format seconds into a readable time string (HH:MM:SS).
    
    Args:
        seconds (float): Time in seconds
    
    Returns:
        str: Formatted time string
    """
    if seconds < 0:
        return "00:00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def validate_video_file(file_path):
    """
    Validate if the file is a valid video file.
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if os.path.getsize(file_path) == 0:
        return False, "File is empty"
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith('video/'):
        return False, "File is not a video format"
    
    # Check file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension not in valid_extensions:
        return False, f"Unsupported file extension: {file_extension}"
    
    return True, "Valid video file"

def get_file_size_mb(file_path):
    """
    Get file size in megabytes.
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        float: File size in MB
    """
    if not os.path.exists(file_path):
        return 0
    
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)

def clean_text(text):
    """
    Clean and normalize text content.
    
    Args:
        text (str): Input text
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line endings
    text = ' '.join(text.split())
    
    # Remove any control characters
    cleaned = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return cleaned.strip()

def estimate_processing_time(file_size_mb, duration_seconds=None):
    """
    Estimate processing time based on file size and duration.
    
    Args:
        file_size_mb (float): File size in megabytes
        duration_seconds (float, optional): Video duration in seconds
    
    Returns:
        int: Estimated processing time in seconds
    """
    # Base processing time (minimum 30 seconds)
    base_time = 30
    
    # Add time based on file size (roughly 2 seconds per MB)
    size_factor = file_size_mb * 2
    
    # Add time based on duration if available (roughly 0.5 seconds per second of video)
    duration_factor = (duration_seconds * 0.5) if duration_seconds else 0
    
    total_time = base_time + size_factor + duration_factor
    
    # Cap at reasonable maximum (10 minutes)
    return min(int(total_time), 600)

def create_safe_filename(filename):
    """
    Create a safe filename by removing/replacing problematic characters.
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Safe filename
    """
    if not filename:
        return "output"
    
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Replace problematic characters
    safe_chars = []
    for char in name_without_ext:
        if char.isalnum() or char in '-_. ':
            safe_chars.append(char)
        else:
            safe_chars.append('_')
    
    safe_name = ''.join(safe_chars).strip()
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "video_summary"
    
    # Limit length
    if len(safe_name) > 50:
        safe_name = safe_name[:50].strip()
    
    return safe_name

def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
