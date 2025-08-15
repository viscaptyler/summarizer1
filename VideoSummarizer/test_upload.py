#!/usr/bin/env python3
"""
Test script to verify the video processing pipeline works with the CV video.
"""
import os
import sys
import tempfile
from video_processor import VideoProcessor
from pdf_generator import PDFGenerator
from ad_analyzer import AdAnalyzer
from video_compressor import VideoCompressor
from utils import get_file_size_mb, validate_video_file

def test_video_pipeline(video_path):
    """Test the complete video processing pipeline."""
    print(f"🧪 Testing video pipeline with: {video_path}")
    
    # Check if file exists and is valid
    if not os.path.exists(video_path):
        print(f"❌ File not found: {video_path}")
        return False
    
    file_size_mb = get_file_size_mb(video_path)
    print(f"📁 File size: {file_size_mb:.1f}MB")
    
    # Validate video file
    is_valid, error_msg = validate_video_file(video_path)
    if not is_valid:
        print(f"❌ Invalid video file: {error_msg}")
        return False
    print(f"✅ Video file validation passed")
    
    try:
        # Initialize processors
        video_processor = VideoProcessor()
        pdf_generator = PDFGenerator()
        ad_analyzer = AdAnalyzer()
        video_compressor = VideoCompressor()
        
        # Test compression (if needed)
        if file_size_mb > 25:
            print(f"📦 Testing compression...")
            compressed_path = video_compressor.compress_video(video_path, target_size_mb=20)
            compressed_size = get_file_size_mb(compressed_path)
            print(f"✅ Compression: {file_size_mb:.1f}MB → {compressed_size:.1f}MB")
            video_path = compressed_path
        
        # Test frame extraction
        print("🎬 Testing frame extraction...")
        frames_data = video_processor.extract_frames(video_path, fps=0.5)
        print(f"✅ Extracted {len(frames_data)} frames")
        
        # Test audio transcription
        print("🎤 Testing audio transcription...")
        transcript = video_processor.transcribe_audio(video_path)
        transcript_length = len(transcript) if transcript else 0
        print(f"✅ Transcription: {transcript_length} characters")
        if transcript:
            print(f"📝 Preview: {transcript[:100]}...")
        
        # Test PDF generation
        print("📄 Testing PDF generation...")
        video_filename = os.path.basename(video_path)
        pdf_path = pdf_generator.create_pdf(frames_data, transcript, video_filename)
        print(f"✅ PDF created: {pdf_path}")
        
        # Test AI analysis
        print("🧠 Testing AI analysis...")
        analysis_text, enhanced_pdf_path = ad_analyzer.process_complete_analysis(
            frames_data, transcript, video_filename
        )
        print(f"✅ AI analysis complete")
        print(f"📊 Analysis length: {len(analysis_text) if analysis_text else 0} characters")
        print(f"📄 Enhanced PDF: {enhanced_pdf_path}")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test with the CV video
    test_video = "test_cv_video.mov"
    success = test_video_pipeline(test_video)
    
    if success:
        print("\n✅ Video processing pipeline is working correctly!")
        print("The Streamlit app should be able to process uploaded videos.")
    else:
        print("\n❌ There are issues with the video processing pipeline.")
        print("Check the errors above and fix them before using the app.")