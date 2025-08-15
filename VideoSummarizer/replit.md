# Video Ad Intelligence Analyzer

## Overview
An advanced AI-powered Video Ad Intelligence Analyzer that transforms marketing video analysis through deep psychological insights and comprehensive reporting. The tool processes video files and generates detailed marketing intelligence reports with frame-by-frame analysis, audio transcription, and AI-powered insights using direct response marketing principles.

## Project Architecture
- **Frontend**: Streamlit web application
- **AI Analysis**: Claude AI (Anthropic) for marketing analysis
- **Video Processing**: FFmpeg for frame extraction and audio processing
- **Audio transcription**: OpenAI Whisper API
- **PDF Generation**: ReportLab for professional reports
- **File Support**: MP4 and MOV video files up to 500MB (auto-compressed if over 50MB)

## Key Features
- Video file upload (MP4, MOV formats supported)
- Frame extraction at 1 frame per 2 seconds
- Audio transcription using OpenAI Whisper
- AI-powered marketing analysis using direct response principles
- Comprehensive PDF report generation
- Professional UI with creator attribution

## Recent Changes
- **2025-06-12**: Added MOV file support alongside MP4
- **2025-06-12**: Added creator credit "@viscaptyler" at top of application
- **2025-07-10**: Added compute optimization features (lazy loading, cleanup, reduced idle usage)
- **2025-07-08**: Increased file limit to 500MB with automatic compression for files over 50MB
- **2025-06-12**: Fixed server configuration to properly enforce 50MB file limit
- **Previous**: Enhanced image display with proper aspect ratio handling
- **Previous**: Removed expert intro sections from AI analysis
- **Previous**: Added complete transcript section to all PDFs

## User Preferences
- Keep AI analysis streamlined without expert introductions
- Include full transcript in plain text at end of PDFs
- Maintain professional UI with creator attribution
- Support both MP4 and MOV video formats
- Support files up to 100MB (reduced from 500MB for cost optimization)
- Optimize compute usage through lazy loading and cleanup
- Minimize background resource consumption

## Technical Notes
- Uses ffmpeg for video processing (supports both MP4 and MOV natively)
- OpenAI Whisper API for audio transcription
- Claude AI for marketing analysis following direct response principles
- ReportLab for PDF generation with proper image handling
- Streamlit app configured to run on port 5000