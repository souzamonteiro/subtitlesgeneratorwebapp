#!/usr/bin/env python3
"""
Command-line tool for extracting audio from videos and generating transcripts/subtitles using Vosk.

This script processes all video files in a given directory, extracts their audio,
performs speech recognition using the Vosk library, and generates both plain text
transcripts and SRT subtitle files.
"""

import argparse
import os
import sys
import json
import subprocess
import wave
from pathlib import Path
from vosk import Model, KaldiRecognizer

def extract_audio(video_path, output_path):
    """
    Extract audio from video file using FFmpeg.
    
    Args:
        video_path (str): Path to the input video file
        output_path (str): Path where the extracted audio will be saved
    """
    try:
        subprocess.run([
            'ffmpeg', '-i', video_path,
            '-ar', '16000', '-ac', '1',
            '-acodec', 'pcm_s16le',
            output_path, '-y'
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to extract audio from {video_path}")

def transcribe_audio(model_path, audio_path):
    """
    Transcribe audio file using Vosk model.
    
    Args:
        model_path (str): Path to the Vosk model directory
        audio_path (str): Path to the audio file to transcribe
        
    Returns:
        list: List of transcription segments with timing information
    """
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        wf.close()
        raise ValueError("Audio file must be WAV format mono PCM.")
    
    segments = []
    chunk_size = 4000
    
    while True:
        data = wf.readframes(chunk_size)
        if len(data) == 0:
            break
            
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if 'text' in result and result['text'].strip():
                segments.append(result)
    
    # Final result
    final_result = recognizer.FinalResult()
    final_json = json.loads(final_result)
    if 'text' in final_json and final_json['text'].strip():
        segments.append(final_json)
    
    wf.close()
    return segments

def generate_srt(segments):
    """
    Generate SRT subtitle content from transcription segments.
    
    Args:
        segments (list): List of transcription segments
        
    Returns:
        str: Formatted SRT content
    """
    def format_time(seconds):
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    srt_lines = []
    cumulative_time = 0
    
    for i, segment in enumerate(segments):
        # Estimate timing based on word count
        words = segment['text'].split()
        duration = max(1.0, len(words) * 0.45)  # Rough estimate of duration per word
        
        start_time = cumulative_time
        end_time = cumulative_time + duration
        
        srt_lines.extend([
            str(i + 1),
            f"{format_time(start_time)} --> {format_time(end_time)}",
            segment['text'],
            ""
        ])
        
        cumulative_time = end_time
    
    return "\n".join(srt_lines)

def process_video_files(input_dir, output_dir, model_path):
    """
    Process all video files in a directory.
    
    Args:
        input_dir (str): Directory containing video files
        output_dir (str): Directory to save transcripts and subtitles
        model_path (str): Path to Vosk model
    """
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all video files
    video_files = [f for f in input_path.iterdir() if f.suffix.lower() in video_extensions]
    
    if not video_files:
        print("No video files found in the specified directory.")
        return
    
    print(f"Found {len(video_files)} video files. Processing...")
    
    for video_file in video_files:
        try:
            print(f"Processing: {video_file.name}")
            
            # Define paths for temporary audio and output files
            audio_file = output_path / f"{video_file.stem}.wav"
            txt_file = output_path / f"{video_file.stem}.txt"
            srt_file = output_path / f"{video_file.stem}.srt"
            
            # Extract audio
            print("  Extracting audio...")
            extract_audio(str(video_file), str(audio_file))
            
            # Transcribe audio
            print("  Transcribing audio...")
            segments = transcribe_audio(model_path, str(audio_file))
            
            # Generate full transcript
            full_transcript = " ".join([seg['text'] for seg in segments if 'text' in seg])
            
            # Save text transcript
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(full_transcript)
            
            # Generate and save SRT
            srt_content = generate_srt(segments)
            with open(srt_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            # Clean up temporary audio file
            audio_file.unlink()
            
            print(f"  Saved: {txt_file.name}, {srt_file.name}")
            
        except Exception as e:
            print(f"  Error processing {video_file.name}: {e}")
    
    print("Processing complete.")

def main():
    """Main function to parse arguments and start processing."""
    parser = argparse.ArgumentParser(
        description="Extract audio from videos and generate transcripts/subtitles using Vosk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -m /path/to/vosk-model -i /input/videos -o /output/transcripts
  %(prog)s --model ./model --input ./videos --output ./subs
        """
    )
    
    parser.add_argument(
        '-m', '--model',
        required=True,
        help='Path to Vosk model directory'
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input directory containing video files'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output directory for transcripts and subtitles'
    )
    
    args = parser.parse_args()
    
    # Validate paths
    if not os.path.exists(args.model):
        print(f"Error: Model path '{args.model}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Check for FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: FFmpeg is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)
    
    # Process videos
    process_video_files(args.input, args.output, args.model)

if __name__ == "__main__":
    main()
