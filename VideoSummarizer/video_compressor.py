import os
import tempfile
import subprocess
from utils import get_file_size_mb

class VideoCompressor:
    def __init__(self):
        """Initialize video compressor."""
        pass
    
    def compress_video(self, input_path, target_size_mb=45, max_duration_seconds=300):
        """
        Compress video to target size while maintaining quality.
        
        Args:
            input_path (str): Path to input video
            target_size_mb (int): Target file size in MB (default: 45MB)
            max_duration_seconds (int): Maximum duration to process (default: 5 minutes)
        
        Returns:
            str: Path to compressed video file
        """
        try:
            # Get original file info
            original_size_mb = get_file_size_mb(input_path)
            
            # If file is already small enough, return original
            if original_size_mb <= target_size_mb:
                return input_path
            
            # Get video duration
            duration = self._get_video_duration(input_path)
            
            # If video is too long, trim it
            if duration > max_duration_seconds:
                print(f"Video duration ({duration}s) exceeds maximum ({max_duration_seconds}s). Trimming...")
                input_path = self._trim_video(input_path, max_duration_seconds)
                duration = max_duration_seconds
            
            # Calculate target bitrate
            target_bitrate_kbps = int((target_size_mb * 8 * 1024) / duration)
            
            # Ensure minimum quality
            min_bitrate = 200  # kbps
            target_bitrate_kbps = max(target_bitrate_kbps, min_bitrate)
            
            # Create compressed video
            compressed_path = self._compress_with_ffmpeg(input_path, target_bitrate_kbps)
            
            compressed_size_mb = get_file_size_mb(compressed_path)
            print(f"Compression complete: {original_size_mb:.1f}MB → {compressed_size_mb:.1f}MB")
            
            return compressed_path
            
        except Exception as e:
            print(f"Error compressing video: {e}")
            return input_path  # Return original if compression fails
    
    def _get_video_duration(self, video_path):
        """Get video duration in seconds."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                return float(data['format']['duration'])
            return 0
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return 0
    
    def _trim_video(self, input_path, max_duration):
        """Trim video to maximum duration."""
        try:
            file_extension = os.path.splitext(input_path)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                trimmed_path = tmp_file.name
            
            cmd = [
                'ffmpeg', '-i', input_path, '-t', str(max_duration),
                '-c', 'copy', '-y', trimmed_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return trimmed_path
            else:
                print(f"Error trimming video: {result.stderr}")
                return input_path
                
        except Exception as e:
            print(f"Error trimming video: {e}")
            return input_path
    
    def _compress_with_ffmpeg(self, input_path, target_bitrate_kbps):
        """Compress video using ffmpeg with specified bitrate."""
        try:
            file_extension = os.path.splitext(input_path)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                compressed_path = tmp_file.name
            
            # Use two-pass encoding for better quality
            cmd_pass1 = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264', '-b:v', f'{target_bitrate_kbps}k',
                '-pass', '1', '-c:a', 'aac', '-b:a', '64k',
                '-f', 'null', '-y', '/dev/null'
            ]
            
            cmd_pass2 = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264', '-b:v', f'{target_bitrate_kbps}k',
                '-pass', '2', '-c:a', 'aac', '-b:a', '64k',
                '-movflags', '+faststart', '-y', compressed_path
            ]
            
            # First pass
            result1 = subprocess.run(cmd_pass1, capture_output=True, text=True)
            if result1.returncode != 0:
                print(f"First pass failed: {result1.stderr}")
                # Fall back to single-pass encoding
                return self._compress_single_pass(input_path, target_bitrate_kbps)
            
            # Second pass
            result2 = subprocess.run(cmd_pass2, capture_output=True, text=True)
            if result2.returncode != 0:
                print(f"Second pass failed: {result2.stderr}")
                return self._compress_single_pass(input_path, target_bitrate_kbps)
            
            # Clean up pass files
            for pass_file in ['ffmpeg2pass-0.log', 'ffmpeg2pass-0.log.mbtree']:
                if os.path.exists(pass_file):
                    os.remove(pass_file)
            
            return compressed_path
            
        except Exception as e:
            print(f"Error in two-pass compression: {e}")
            return self._compress_single_pass(input_path, target_bitrate_kbps)
    
    def _compress_single_pass(self, input_path, target_bitrate_kbps):
        """Single-pass compression as fallback."""
        try:
            file_extension = os.path.splitext(input_path)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                compressed_path = tmp_file.name
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264', '-b:v', f'{target_bitrate_kbps}k',
                '-c:a', 'aac', '-b:a', '64k',
                '-movflags', '+faststart', '-y', compressed_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return compressed_path
            else:
                print(f"Single-pass compression failed: {result.stderr}")
                return input_path
                
        except Exception as e:
            print(f"Error in single-pass compression: {e}")
            return input_path