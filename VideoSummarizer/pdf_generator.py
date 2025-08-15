import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import textwrap
from utils import format_time
from io import BytesIO

class PDFGenerator:
    def __init__(self):
        """Initialize PDF generator with styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkgrey
        )
        
        # Timestamp style
        self.timestamp_style = ParagraphStyle(
            'TimestampStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.blue,
            fontName='Helvetica-Bold'
        )
        
        # Transcript style
        self.transcript_style = ParagraphStyle(
            'TranscriptStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=20,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=10
        )
        
        # Frame caption style
        self.caption_style = ParagraphStyle(
            'CaptionStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.darkgrey,
            fontName='Helvetica-Oblique'
        )
        
        # Full transcript style
        self.full_transcript_style = ParagraphStyle(
            'FullTranscriptStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leftIndent=15,
            rightIndent=15,
            spaceBefore=6
        )
    
    def create_pdf(self, frames_data, transcript_text, video_filename):
        """
        Create PDF with frames and transcript.
        
        Args:
            frames_data (list): List of frame dictionaries
            transcript_text (str): Full transcript text
            video_filename (str): Original video filename
        
        Returns:
            str: Path to the generated PDF file
        """
        # Create temporary PDF file
        pdf_path = tempfile.mktemp(suffix='.pdf')
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build PDF content
        story = []
        
        # Add title page
        story.extend(self._create_title_page(video_filename, len(frames_data)))
        
        # Add frames and transcript sections
        story.extend(self._create_content_pages(frames_data, transcript_text))
        
        # Add full transcript section at the end
        story.extend(self._create_full_transcript_section(transcript_text))
        
        # Build PDF 
        doc.build(story)
        
        return pdf_path
    
    def _create_title_page(self, video_filename, frame_count):
        """Create the title page of the PDF."""
        story = []
        
        # Main title
        title = Paragraph("📹 Video Summary Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Video information
        video_info = f"""
        <b>Original File:</b> {video_filename}<br/>
        <b>Frames Extracted:</b> {frame_count}<br/>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Processing:</b> 1 frame per second with audio transcription
        """
        
        info_para = Paragraph(video_info, self.subtitle_style)
        story.append(info_para)
        story.append(Spacer(1, 1*inch))
        
        # Description
        description = """
        This document contains a comprehensive summary of your video file, including:
        <br/><br/>
        • Visual timeline with key frames extracted at 1-second intervals<br/>
        • Complete audio transcription synchronized with timestamps<br/>
        • Clean, readable layout for easy reference<br/>
        """
        
        desc_para = Paragraph(description, self.styles['Normal'])
        story.append(desc_para)
        story.append(PageBreak())
        
        return story
    
    def _create_content_pages(self, frames_data, transcript_text):
        """Create content pages with frames and transcript."""
        story = []
        
        # If we have frames, create frame-based pages
        if frames_data:
            story.extend(self._create_frame_pages(frames_data, transcript_text))
        else:
            # If no frames, just add transcript
            story.extend(self._create_transcript_only_pages(transcript_text))
        
        return story
    
    def _create_frame_pages(self, frames_data, transcript_text):
        """Create pages with frames and corresponding transcript sections."""
        story = []
        
        # Calculate transcript segments for each frame
        if transcript_text and len(frames_data) > 1:
            # Estimate transcript segments based on timestamps
            transcript_segments = self._segment_transcript(transcript_text, frames_data)
        else:
            # If only one frame or no transcript, use full text
            transcript_segments = [transcript_text] * len(frames_data)
        
        for i, frame_data in enumerate(frames_data):
            # Add frame title
            timestamp = frame_data['timestamp']
            frame_title = f"Frame at {format_time(timestamp)}"
            title_para = Paragraph(frame_title, self.timestamp_style)
            story.append(title_para)
            story.append(Spacer(1, 0.2*inch))
            
            # Add frame image
            try:
                # Use BytesIO to create image directly from memory
                image_stream = BytesIO(frame_data['image_data'])
                
                # Create PIL Image to get actual dimensions
                from PIL import Image as PILImage
                pil_img = PILImage.open(image_stream)
                original_width, original_height = pil_img.size
                pil_img.close()
                
                # Reset stream position
                image_stream.seek(0)
                
                # Calculate proper aspect ratio
                aspect_ratio = original_width / original_height
                
                # Set maximum dimensions
                max_width = 5*inch
                max_height = 3.5*inch
                
                # Calculate dimensions maintaining aspect ratio
                if aspect_ratio > (max_width / max_height):
                    # Image is wider - constrain by width
                    img_width = max_width
                    img_height = max_width / aspect_ratio
                else:
                    # Image is taller - constrain by height
                    img_height = max_height
                    img_width = max_height * aspect_ratio
                
                # Add image to PDF with calculated dimensions
                img = Image(image_stream, width=img_width, height=img_height)
                story.append(img)
                
                # Add image caption
                caption = f"Video frame at {format_time(timestamp)}"
                caption_para = Paragraph(caption, self.caption_style)
                story.append(caption_para)
                story.append(Spacer(1, 0.3*inch))
                
            except Exception as e:
                error_text = f"Error displaying frame: {str(e)}"
                error_para = Paragraph(error_text, self.styles['Normal'])
                story.append(error_para)
                story.append(Spacer(1, 0.2*inch))
            
            # Add corresponding transcript segment
            if i < len(transcript_segments) and transcript_segments[i]:
                transcript_title = Paragraph("📝 Transcript", self.styles['Heading3'])
                story.append(transcript_title)
                
                # Wrap and format transcript text
                segment_text = transcript_segments[i].strip()
                if segment_text:
                    # Break long text into paragraphs
                    paragraphs = self._format_transcript_text(segment_text)
                    for para_text in paragraphs:
                        para = Paragraph(para_text, self.transcript_style)
                        story.append(para)
                else:
                    no_audio_para = Paragraph("No audio detected for this time segment.", self.transcript_style)
                    story.append(no_audio_para)
            
            # Add page break (except for the last frame)
            if i < len(frames_data) - 1:
                story.append(PageBreak())
        
        return story
    
    def _create_transcript_only_pages(self, transcript_text):
        """Create pages with only transcript when no frames are available."""
        story = []
        
        # Add transcript title
        title = Paragraph("📝 Complete Transcript", self.styles['Heading2'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        if transcript_text:
            paragraphs = self._format_transcript_text(transcript_text)
            for para_text in paragraphs:
                para = Paragraph(para_text, self.transcript_style)
                story.append(para)
        else:
            no_transcript_para = Paragraph("No transcript available.", self.transcript_style)
            story.append(no_transcript_para)
        
        return story
    
    def _segment_transcript(self, transcript_text, frames_data):
        """
        Segment transcript text based on frame timestamps.
        
        Args:
            transcript_text (str): Full transcript
            frames_data (list): Frame data with timestamps
        
        Returns:
            list: List of transcript segments
        """
        if not transcript_text or len(frames_data) <= 1:
            return [transcript_text]
        
        # Simple segmentation - divide transcript equally among frames
        # In a more sophisticated version, you could use timestamp data from Whisper
        words = transcript_text.split()
        words_per_segment = max(1, len(words) // len(frames_data))
        
        segments = []
        for i in range(len(frames_data)):
            start_idx = i * words_per_segment
            end_idx = start_idx + words_per_segment
            
            # For the last segment, include all remaining words
            if i == len(frames_data) - 1:
                segment_words = words[start_idx:]
            else:
                segment_words = words[start_idx:end_idx]
            
            segments.append(' '.join(segment_words))
        
        return segments
    
    def _format_transcript_text(self, text):
        """
        Format transcript text into readable paragraphs.
        
        Args:
            text (str): Raw transcript text
        
        Returns:
            list: List of formatted paragraph strings
        """
        if not text:
            return [""]
        
        # Split into sentences
        sentences = text.replace('. ', '.|').replace('? ', '?|').replace('! ', '!|').split('|')
        
        paragraphs = []
        current_paragraph = []
        words_in_paragraph = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            words_in_sentence = len(sentence.split())
            
            # Start new paragraph if current one is getting too long
            if words_in_paragraph > 100 and current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
                words_in_paragraph = 0
            
            current_paragraph.append(sentence)
            words_in_paragraph += words_in_sentence
        
        # Add the last paragraph
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        return paragraphs if paragraphs else [text]
    
    def _create_full_transcript_section(self, transcript_text):
        """Create a section with the complete transcript."""
        story = []
        
        # Add page break
        story.append(PageBreak())
        
        # Add section title
        title = Paragraph("📋 Complete Transcript", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Add full transcript
        if transcript_text:
            formatted_paragraphs = self._format_transcript_text(transcript_text)
            for para_text in formatted_paragraphs:
                if para_text.strip():
                    para = Paragraph(para_text, self.full_transcript_style)
                    story.append(para)
                    story.append(Spacer(1, 0.1*inch))
        else:
            no_transcript = Paragraph("No transcript available", self.full_transcript_style)
            story.append(no_transcript)
        
        return story
    

