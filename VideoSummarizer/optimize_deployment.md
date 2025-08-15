# Compute Optimization Guide

## Current Issues
- Streamlit server runs continuously (even when idle)
- AI models (Claude, OpenAI) loaded in memory 
- FFmpeg processes remain active
- Session state persists across requests

## Optimization Strategies

### 1. Lazy Loading (Implemented)
- Only initialize AI processors when analysis starts
- Reduces idle memory usage

### 2. Process Cleanup
- Clean up temporary files after each request
- Terminate FFmpeg processes when done
- Clear session state after completion

### 3. Deployment Options
- **Current**: Always-on autoscale (expensive for low traffic)
- **Better**: Manual deployment (only runs when accessed)
- **Best**: Static hosting + serverless functions for processing

### 4. Resource Limits
- Set memory limits in deployment
- Use lower-resolution frame extraction for demos
- Compress videos more aggressively

### 5. Caching Strategy
- Cache processed results to avoid reprocessing
- Store compressed videos temporarily
- Reuse AI analysis for similar content

## Recommended Changes
1. Switch to manual deployment for demo/testing
2. Add automatic cleanup after processing
3. Implement result caching
4. Use smaller AI models for demos
5. Add timeout limits for long processes