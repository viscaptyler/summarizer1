import streamlit as st
import os
import tempfile
import time
from video_processor import VideoProcessor
from pdf_generator import PDFGenerator
from ad_analyzer import AdAnalyzer
from video_compressor import VideoCompressor
from utils import format_time, validate_video_file, get_file_size_mb

st.set_page_config(
    page_title="Video Ad Intelligence Analyzer",
    page_icon="🧠",
    layout="wide"
)

st.markdown("*Created by @viscaptyler*")
st.title("🧠 Video Ad Intelligence Analyzer")
st.markdown("**Transform any video ad into actionable marketing intelligence.** Get frame-by-frame breakdowns, accurate transcripts, and expert analysis using proven $142M+ direct response frameworks.")

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

# Reduce idle CPU usage when not processing
if not st.session_state.processing:
    time.sleep(0.1)  # Small delay to reduce CPU cycles

# File upload section
st.header("🎯 Upload Your Video Ad")
st.markdown("**Get instant intelligence on any video ad.** Upload and watch our AI dissect the psychology, triggers, and frameworks that drive conversions.")

# Already configured in config.toml

try:
    uploaded_file = st.file_uploader(
        "Drop your video file here",
        type=['mp4', 'mov'],
        help="Maximum: 150MB • Files over 25MB will be compressed automatically • Supports MP4 & MOV"
    )
except Exception as e:
    if "413" in str(e) or "Request Entity Too Large" in str(e):
        st.error("🚫 File too large! The file you're trying to upload exceeds server limits.")
        st.info("💡 **Solutions:**")
        st.info("• Try compressing your video to under 150MB first")
        st.info("• Use a video compression tool like HandBrake or online compressors")
        st.info("• Upload a shorter clip (under 3-4 minutes)")
        uploaded_file = None
    else:
        st.error(f"Upload error: {str(e)}")
        uploaded_file = None

if uploaded_file is not None:
    # Validate file size (100MB limit with auto-compression)
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    
    if file_size_mb > 150:
        st.error(f"File size ({file_size_mb:.1f}MB) exceeds the 150MB limit. Please upload a smaller file.")
        st.info("💡 **Quick fix:** Videos over 150MB are typically very long or high resolution. Try reducing length or quality.")
    else:
        st.success(f"Video locked and loaded! Size: {file_size_mb:.1f}MB")
        
        # Add compression notification
        if file_size_mb > 25:
            st.info("📦 Files over 25MB will be automatically compressed to optimize processing time.")
            st.info("⏱️ Videos longer than 5 minutes will be trimmed to the first 5 minutes for analysis.")
        
        # Display file information
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Filename:** {uploaded_file.name}")
        with col2:
            st.info(f"**Size:** {file_size_mb:.1f}MB")
        
        # Process buttons
        col1, col2 = st.columns(2)
        with col1:
            analyze_button = st.button("🧠 Full Analysis", disabled=st.session_state.processing)
        with col2:
            transcribe_button = st.button("🎤 Transcribe Only", disabled=st.session_state.processing)
        
        if analyze_button or transcribe_button:
            st.session_state.processing = True
            st.session_state.processed_data = None
            
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            video_path = None
            try:
                # Save uploaded file to temporary location with correct extension
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                if file_extension not in ['.mp4', '.mov']:
                    file_extension = '.mp4'  # Default fallback
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_video_path = tmp_file.name
                
                # Initialize processors only when needed (lazy loading)
                status_text.text("🔧 Initializing processors...")
                video_processor = VideoProcessor()
                pdf_generator = PDFGenerator()
                ad_analyzer = AdAnalyzer()
                video_compressor = VideoCompressor()
                
                # Check file size and compress if needed
                original_size_mb = get_file_size_mb(temp_video_path)
                if original_size_mb > 25:
                    status_text.text(f"📦 Compressing video ({original_size_mb:.1f}MB → target: 45MB)...")
                    video_path = video_compressor.compress_video(temp_video_path, target_size_mb=45)
                    compressed_size_mb = get_file_size_mb(video_path)
                    status_text.text(f"✅ Compression complete: {original_size_mb:.1f}MB → {compressed_size_mb:.1f}MB")
                    time.sleep(1)  # Brief pause to show compression result
                else:
                    video_path = temp_video_path
                
                # Determine processing mode
                transcribe_only = transcribe_button if 'transcribe_button' in locals() else False
                
                frames_data = []
                if not transcribe_only:
                    # Step 1: Extract frames (only for full analysis)
                    status_text.text("🎬 Extracting key frames...")
                    progress_bar.progress(20)
                    
                    frames_data = video_processor.extract_frames(video_path, fps=0.5)  # 1 frame every 2 seconds
                    
                    if not frames_data:
                        st.error("Failed to extract frames from the video. Please ensure the file is a valid video.")
                        st.session_state.processing = False
                        st.stop()
                else:
                    # Skip frame extraction for transcription-only
                    progress_bar.progress(30)
                
                # Step 2: Transcribe audio
                status_text.text("🎤 Extracting speech patterns...")
                progress_bar.progress(50)
                
                transcript_data = video_processor.transcribe_audio(video_path)
                
                # Handle transcription errors but continue with PDF generation
                if not transcript_data or "failed" in transcript_data.lower() or "recognition failed" in transcript_data.lower():
                    st.warning("⚠️ Audio transcription failed. Continuing with visual-only analysis.")
                    transcript_data = "Transcript unavailable: Audio transcription failed. This could be due to unclear audio, background noise, or network connectivity issues. The analysis will focus on visual elements with timestamps."
                
                # Step 3: AI Analysis and PDF Generation (skip for transcription-only)
                pdf_path = None
                analysis_text = None
                enhanced_pdf_path = None
                
                if transcribe_only:
                    # Transcription-only mode - skip AI analysis and PDF generation
                    status_text.text("🎤 Transcription complete!")
                    progress_bar.progress(100)
                elif os.getenv("ANTHROPIC_API_KEY"):
                    status_text.text("🧠 Applying $142M marketing framework...")
                    progress_bar.progress(85)
                    
                    try:
                        analysis_text, enhanced_pdf_path = ad_analyzer.process_complete_analysis(frames_data, transcript_data, uploaded_file.name)
                        if enhanced_pdf_path and os.path.exists(enhanced_pdf_path):
                            pdf_path = enhanced_pdf_path  # Use the comprehensive PDF as the main PDF
                        else:
                            raise Exception("Enhanced PDF creation failed")
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"AI Analysis failed: {error_msg}")
                        
                        # Show specific error for debugging
                        if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                            st.error("Anthropic API key issue detected. Please check your API key configuration.")
                        elif "quota" in error_msg.lower() or "429" in error_msg:
                            st.error("Anthropic API quota exceeded. Please check your billing.")
                        
                        # Fallback to basic PDF if AI analysis fails
                        status_text.text("📄 Creating basic visual breakdown...")
                        try:
                            pdf_path = pdf_generator.create_pdf(frames_data, transcript_data, uploaded_file.name)
                        except Exception as pdf_error:
                            st.error(f"PDF creation failed: {str(pdf_error)}")
                            pdf_path = None
                        analysis_text = None
                        enhanced_pdf_path = None
                else:
                    # No AI analysis available, create basic PDF
                    status_text.text("📄 Creating visual breakdown...")
                    progress_bar.progress(85)
                    try:
                        pdf_path = pdf_generator.create_pdf(frames_data, transcript_data, uploaded_file.name)
                    except Exception as pdf_error:
                        st.error(f"PDF creation failed: {str(pdf_error)}")
                        pdf_path = None
                
                # Step 4: Complete
                progress_bar.progress(100)
                status_text.text("🎉 Intelligence extraction complete!")
                
                # Store processed data
                st.session_state.processed_data = {
                    'pdf_path': pdf_path,
                    'enhanced_pdf_path': enhanced_pdf_path,
                    'analysis_text': analysis_text,
                    'frames_count': len(frames_data),
                    'transcript_length': len(transcript_data) if transcript_data else 0,
                    'video_filename': uploaded_file.name,
                    'has_ai_analysis': enhanced_pdf_path is not None and pdf_path == enhanced_pdf_path,
                    'transcribe_only': transcribe_only,
                    'transcript_data': transcript_data if transcribe_only else None
                }
                
                # Clean up temporary video file
                os.unlink(video_path)
                
            except Exception as e:
                st.error(f"An error occurred during processing: {str(e)}")
                # Clean up temporary files
                if video_path and os.path.exists(video_path):
                    try:
                        os.unlink(video_path)
                    except:
                        pass
            
            finally:
                # Comprehensive cleanup to reduce memory usage
                try:
                    if 'video_path' in locals() and video_path and os.path.exists(video_path):
                        os.unlink(video_path)
                except:
                    pass
                
                try:
                    if 'temp_video_path' in locals() and temp_video_path and temp_video_path != locals().get('video_path') and os.path.exists(temp_video_path):
                        os.unlink(temp_video_path)
                except:
                    pass
                
                # Force garbage collection to free memory
                import gc
                gc.collect()
                
                st.session_state.processing = False
                time.sleep(1)  # Brief pause to show completion
                st.rerun()

# Display results and download section
if st.session_state.processed_data:
    if st.session_state.processed_data.get('transcribe_only'):
        st.header("🎤 Transcription Results")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Duration", "Processing complete")
        with col2:
            st.metric("Transcript Length", f"{st.session_state.processed_data['transcript_length']} chars")
        
        # Display transcript
        transcript_data = st.session_state.processed_data.get('transcript_data', '')
        if transcript_data and transcript_data.strip():
            st.subheader("📝 Full Transcript")
            st.text_area("Transcript", transcript_data, height=300, disabled=True)
            
            # Download transcript as text file
            st.download_button(
                label="📄 Download Transcript (.txt)",
                data=transcript_data,
                file_name=f"{os.path.splitext(st.session_state.processed_data['video_filename'])[0]}_transcript.txt",
                mime="text/plain"
            )
        else:
            st.warning("No transcript available. Audio transcription may have failed.")
    else:
        st.header("📊 Intelligence Report")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Key Frames", st.session_state.processed_data['frames_count'])
        with col2:
            st.metric("Speech Analysis", f"{st.session_state.processed_data['transcript_length']} chars")
        with col3:
            st.metric("AI Analysis", "Ready 🧠" if st.session_state.processed_data.get('analysis_text') else "Basic Only")
    
        # Download section (only for full analysis)
        st.header("🚀 Your Marketing Intelligence is Ready")
        
        # Generate safe filename
        video_filename = st.session_state.processed_data.get('video_filename', 'video')
        video_name = os.path.splitext(video_filename)[0]
        safe_name = "".join(c for c in video_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Main PDF Download
        pdf_path = st.session_state.processed_data.get('pdf_path')
        has_ai_analysis = st.session_state.processed_data.get('has_ai_analysis', False)
        analysis_text = st.session_state.processed_data.get('analysis_text')
    
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            # Display appropriate title based on content
            if has_ai_analysis:
                st.subheader("🧠 Complete Marketing Intelligence Report")
                st.write("Expert AI analysis + frames + transcript in one comprehensive package")
                download_filename = f"{safe_name}_AI_Analysis.pdf"
                button_label = "Download Complete Intelligence Report"
                help_text = "Complete package: AI marketing analysis + video frames + transcript"
            else:
                st.subheader("📄 Video Summary Report")
                st.write("Video frames + transcript breakdown")
                download_filename = f"{safe_name}_summary.pdf"
                button_label = "Download Video Summary"
                help_text = "Video frames with synchronized transcript"
            
            st.download_button(
                label=button_label,
                data=pdf_bytes,
                file_name=download_filename,
                mime="application/pdf",
                help=help_text,
                use_container_width=True
            )
            
            # Show analysis preview if available
            if has_ai_analysis and analysis_text:
                with st.expander("Preview AI Marketing Analysis", expanded=False):
                    st.write(analysis_text[:800] + "..." if len(analysis_text) > 800 else analysis_text)
            
            # Status message
            if has_ai_analysis:
                st.success("🎉 Your complete marketing intelligence package is ready!")
            else:
                st.success("📄 Your video summary is ready!")
                if not os.getenv("ANTHROPIC_API_KEY"):
                    st.info("💡 Add an Anthropic API key to unlock AI marketing analysis features")
        else:
            st.error("PDF file not found. Please try processing again.")

# Processing indicator
if st.session_state.processing:
    st.info("🧠 Your ad is being analyzed using proven marketing frameworks...")

# Footer information
st.markdown("---")
st.markdown("""
### 🎯 The Intelligence Pipeline:
1. **Upload** your video ad (MP4, max 50MB, recommended under 2 minutes)
2. **Frame Extraction** - Key moments captured every 2 seconds
3. **Speech Analysis** - Professional transcription via OpenAI Whisper
4. **Visual Breakdown** - Comprehensive PDF with frames and transcript
5. **AI Marketing Analysis** - Expert breakdown using $142M+ direct response frameworks
6. **Download** - Complete intelligence package ready for your team

### 🧠 What Makes This Different:
- **Battle-Tested Framework:** Analysis based on $142M+ in real ad spend data
- **Psychological Depth:** Reveals hidden triggers and conversion principles
- **Actionable Intelligence:** Not just analysis - strategic insights you can implement
- **Professional Grade:** The same frameworks used by 8-figure brands

**Perfect for:** Marketing teams, agencies, entrepreneurs, and anyone serious about understanding what makes video ads convert.
""")
