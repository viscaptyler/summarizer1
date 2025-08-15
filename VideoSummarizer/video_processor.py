import os
import tempfile
import subprocess
import json
from PIL import Image
from pydub import AudioSegment
from openai import OpenAI

class VideoProcessor:
    def __init__(self):
        """Initialize the video processor with OpenAI client."""
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "")
        )
    
    def extract_frames(self, video_path, fps=1.0):
        """
        Extract frames from video at specified FPS.
        
        Args:
            video_path (str): Path to the video file
            fps (float): Frames per second to extract (default: 1.0)
        
        Returns:
            list: List of dictionaries containing frame data
        """
        frames_data = []
        
        try:
            # Create temporary directory for frames
            with tempfile.TemporaryDirectory() as temp_dir:
                # Get video duration first
                duration = self._get_video_duration(video_path)
                if duration <= 0:
                    return []
                
                # Extract frames using ffmpeg
                frame_pattern = os.path.join(temp_dir, "frame_%04d.jpg")
                
                cmd = [
                    'ffmpeg', '-i', video_path, '-vf', f'fps={fps}',
                    '-y', frame_pattern
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"FFmpeg frame extraction failed: {result.stderr}")
                    return []
                
                # Process extracted frames
                frame_files = sorted([f for f in os.listdir(temp_dir) if f.startswith('frame_')])
                
                for i, frame_file in enumerate(frame_files):
                    frame_path = os.path.join(temp_dir, frame_file)
                    timestamp = i / fps  # Calculate timestamp based on FPS
                    
                    # Load and process image
                    try:
                        with Image.open(frame_path) as img:
                            # Resize image if too large (max width: 800px)
                            if img.width > 800:
                                ratio = 800 / img.width
                                new_height = int(img.height * ratio)
                                img = img.resize((800, new_height), Image.Resampling.LANCZOS)
                            
                            # Save processed image to temporary location
                            processed_frame_path = os.path.join(temp_dir, f"processed_{frame_file}")
                            img.save(processed_frame_path, 'JPEG', quality=85)
                            
                            # Read image data
                            with open(processed_frame_path, 'rb') as f:
                                image_data = f.read()
                            
                            frames_data.append({
                                'timestamp': timestamp,
                                'image_data': image_data,
                                'filename': f"frame_{i+1:04d}.jpg"
                            })
                    
                    except Exception as e:
                        print(f"Error processing frame {frame_file}: {e}")
                        continue
        
        except Exception as e:
            print(f"Error extracting frames: {e}")
            return []
        
        return frames_data
    
    def transcribe_audio(self, video_path):
        """
        Transcribe audio from video using OpenAI Whisper API.
        
        Args:
            video_path (str): Path to the video file
        
        Returns:
            str: Transcribed text
        """
        audio_path = None
        try:
            # Extract audio from video
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as audio_file:
                audio_path = audio_file.name
            
            # Use ffmpeg to extract audio
            cmd = [
                'ffmpeg', '-i', video_path, '-acodec', 'mp3', 
                '-ac', '1', '-ar', '16000', '-y', audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"FFmpeg audio extraction failed: {result.stderr}")
                return "Failed to extract audio from video."
            
            # Check if audio file was created and has content
            if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                return "No audio content found in the video."
            
            # Try OpenAI Whisper API
            try:
                with open(audio_path, 'rb') as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                
                if audio_path and os.path.exists(audio_path):
                    os.unlink(audio_path)
                
                return transcript if transcript else "No speech detected in the audio."
            
            except Exception as openai_error:
                print(f"OpenAI Whisper failed: {openai_error}")
                error_msg = str(openai_error)
                if "insufficient_quota" in error_msg or "429" in error_msg:
                    return "OpenAI API quota exceeded. Please check your billing or try again later."
                elif "401" in error_msg or "unauthorized" in error_msg.lower():
                    return "OpenAI API key is invalid. Please check your API key configuration."
                else:
                    return f"Transcription failed: {error_msg}"
        
        except Exception as e:
            print(f"Error in transcription process: {e}")
            return f"Transcription failed: {str(e)}"
        
        finally:
            # Clean up temporary files
            if audio_path and os.path.exists(audio_path):
                try:
                    os.unlink(audio_path)
                except:
                    pass
    
    def _get_video_duration(self, video_path):
        """
        Get video duration in seconds.
        
        Args:
            video_path (str): Path to the video file
        
        Returns:
            float: Duration in seconds
        """
        try:
            # Use subprocess to call ffprobe directly
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        duration = float(stream.get('duration', 0))
                        if duration > 0:
                            return duration
            return 0
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return 0
    
    def get_video_info(self, video_path):
        """
        Get basic video information.
        
        Args:
            video_path (str): Path to the video file
        
        Returns:
            dict: Video information
        """
        try:
            # Use subprocess to call ffprobe directly
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                video_stream = next((stream for stream in data.get('streams', []) if stream.get('codec_type') == 'video'), None)
                
                if video_stream:
                    # Parse frame rate safely
                    fps = 0
                    r_frame_rate = video_stream.get('r_frame_rate', '0/1')
                    if '/' in r_frame_rate:
                        try:
                            num, den = map(float, r_frame_rate.split('/'))
                            fps = num / den if den != 0 else 0
                        except:
                            fps = 0
                    
                    return {
                        'duration': float(video_stream.get('duration', 0)),
                        'width': int(video_stream.get('width', 0)),
                        'height': int(video_stream.get('height', 0)),
                        'fps': fps
                    }
        except Exception as e:
            print(f"Error getting video info: {e}")
        
        return {'duration': 0, 'width': 0, 'height': 0, 'fps': 0}
