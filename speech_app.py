import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json
import subprocess
import wave
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

class SpeechRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtitles Generator App")
        self.root.geometry("700x700")
        
        # Variables
        self.audio_file = None
        self.model = None
        self.recognizer = None
        self.is_recording = False
        self.subtitle_segments = []
        self.recording_stream = None
        
        # Model configuration (assuming models are already downloaded)
        # self.models = {
        #     "English": "vosk-model-small-en-us-0.15",
        #     "Spanish": "vosk-model-small-es-0.42",
        #     "Portuguese": "vosk-model-small-pt-0.3"
        # }
        self.models = {
            "English": "vosk-model-en-us-0.22",
            "Spanish": "vosk-model-es-0.42",
            "Portuguese": "vosk-model-pt-fb-v0.1.1-20220516_2113"
        }
        
        self.setup_ui()
        self.check_models()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Subtitles Generator App", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Button(main_frame, text="Select Audio File", command=self.select_file).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_label = ttk.Label(main_frame, text="No file selected")
        self.file_label.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Language selection
        ttk.Label(main_frame, text="Language:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.lang_var = tk.StringVar(value="English")
        lang_combo = ttk.Combobox(main_frame, textvariable=self.lang_var, values=list(self.models.keys()), state="readonly")
        lang_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Load Model", command=self.load_model_thread).pack(side=tk.LEFT, padx=(0, 5))
        self.mic_btn = ttk.Button(button_frame, text="Use Microphone", command=self.toggle_microphone)
        self.mic_btn.pack(side=tk.LEFT, padx=5)
        self.process_btn = ttk.Button(button_frame, text="Process Audio", command=self.process_audio_thread, state=tk.DISABLED)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download SRT", command=self.download_srt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_app).pack(side=tk.LEFT, padx=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Transcript area
        ttk.Label(main_frame, text="Recognized Text:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        self.transcript_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.transcript_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.transcript_text.yview)
        scrollbar.grid(row=7, column=3, sticky=(tk.N, tk.S))
        self.transcript_text.configure(yscrollcommand=scrollbar.set)
        
        # Subtitle area
        ttk.Label(main_frame, text="Subtitles:", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=(10, 5))
        self.subtitle_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        self.subtitle_text.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        sub_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.subtitle_text.yview)
        sub_scrollbar.grid(row=9, column=3, sticky=(tk.N, tk.S))
        self.subtitle_text.configure(yscrollcommand=sub_scrollbar.set)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        main_frame.rowconfigure(9, weight=1)
    
    def check_models(self):
        """Check if models exist locally"""
        model_dir = "models"
        missing_models = []
        
        if not os.path.exists(model_dir):
            self.update_status("Models directory not found")
            return False
            
        for lang, model_name in self.models.items():
            model_path = os.path.join(model_dir, model_name)
            if not os.path.exists(model_path):
                missing_models.append(lang)
        
        if missing_models:
            self.update_status(f"Missing models: {', '.join(missing_models)}")
            return False
        else:
            self.update_status("All models found locally")
            return True
    
    def select_file(self):
        """Open file dialog to select audio file"""
        filetypes = (
            ("Audio files", "*.wav *.mp3 *.ogg *.flac"),
            ("All files", "*.*")
        )
        filename = filedialog.askopenfilename(title="Select Audio File", filetypes=filetypes)
        if filename:
            self.audio_file = filename
            self.file_label.config(text=os.path.basename(filename))
            self.update_status("File selected")
    
    def load_model_thread(self):
        """Load model in separate thread"""
        self.progress.start()
        threading.Thread(target=self.load_model, daemon=True).start()
    
    def load_model(self):
        """Load Vosk model"""
        try:
            lang = self.lang_var.get()
            model_path = os.path.join("models", self.models[lang])
            
            if not os.path.exists(model_path):
                self.update_status(f"Model not found: {model_path}")
                return
                
            self.update_status("Loading model...")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.process_btn.config(state=tk.NORMAL)
            self.update_status("Model loaded successfully")
        except Exception as e:
            self.update_status(f"Error loading model: {str(e)}")
        finally:
            self.progress.stop()
    
    def toggle_microphone(self):
        """Toggle microphone recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start microphone recording"""
        if not self.model:
            self.update_status("Load model first")
            return
            
        self.is_recording = True
        self.mic_btn.config(text="Stop Microphone")
        self.subtitle_segments = []
        self.transcript_text.delete(1.0, tk.END)
        self.subtitle_text.delete(1.0, tk.END)
        
        self.update_status("Recording... Speak now")
        
        # Start recording
        try:
            def audio_callback(indata, frames, time, status):
                if self.is_recording and self.recognizer:
                    # Process audio chunk
                    audio_chunk = indata[:, 0].astype(np.float32)
                    if self.recognizer.AcceptWaveform(audio_chunk):
                        result = json.loads(self.recognizer.Result())
                        if 'text' in result and result['text']:
                            self.root.after(0, self.update_transcript, result['text'])
                            self.root.after(0, self.add_subtitle_segment, result)
                    else:
                        partial = self.recognizer.PartialResult()
                        partial_result = json.loads(partial)
                        if 'partial' in partial_result:
                            self.root.after(0, self.update_partial_transcript, partial_result['partial'])
            
            self.recording_stream = sd.InputStream(
                samplerate=16000,
                channels=1,
                dtype=np.float32,
                callback=audio_callback
            )
            self.recording_stream.start()
        except Exception as e:
            self.update_status(f"Recording error: {str(e)}")
    
    def stop_recording(self):
        """Stop microphone recording"""
        self.is_recording = False
        self.mic_btn.config(text="Use Microphone")
        
        # Stop recording stream
        if self.recording_stream:
            self.recording_stream.stop()
            self.recording_stream.close()
            self.recording_stream = None
            
        self.update_status("Recording stopped")
    
    def process_audio_thread(self):
        """Process audio file in separate thread"""
        if not self.audio_file:
            self.update_status("No audio file selected")
            return
            
        self.progress.start()
        threading.Thread(target=self.process_audio, daemon=True).start()
    
    def process_audio(self):
        """Process selected audio file"""
        try:
            self.update_status("Processing audio...")
            self.transcript_text.delete(1.0, tk.END)
            self.subtitle_text.delete(1.0, tk.END)
            self.subtitle_segments = []
            
            # Convert to WAV if needed
            wav_file = self.convert_to_wav(self.audio_file)
            
            # Open audio file
            wf = wave.open(wav_file, "rb")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                wf.close()
                raise ValueError("Audio file must be WAV format mono PCM.")
            
            # Process audio chunks
            chunk_size = 4000
            sample_rate = wf.getframerate()
            
            while True:
                data = wf.readframes(chunk_size)
                if len(data) == 0:
                    break
                    
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if 'text' in result and result['text']:
                        self.root.after(0, self.update_transcript, result['text'])
                        self.root.after(0, self.add_subtitle_segment, result)
                        
            # Final result
            final_result = self.recognizer.FinalResult()
            final_json = json.loads(final_result)
            if 'text' in final_json and final_json['text']:
                self.root.after(0, self.update_transcript, final_json['text'])
                self.root.after(0, self.add_subtitle_segment, final_json)
                
            wf.close()
            self.update_status("Processing complete")
        except Exception as e:
            self.update_status(f"Processing error: {str(e)}")
        finally:
            self.progress.stop()
    
    def convert_to_wav(self, input_file):
        """Convert audio file to WAV format"""
        output_file = "temp_audio.wav"
        try:
            # Use ffmpeg to convert
            subprocess.run([
                "ffmpeg", "-i", input_file, 
                "-ar", "16000", "-ac", "1", 
                "-acodec", "pcm_s16le", 
                output_file, "-y"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_file
        except:
            # Fallback: assume it's already WAV
            return input_file
    
    def update_transcript(self, text):
        """Update transcript text area"""
        current = self.transcript_text.get(1.0, tk.END).strip()
        if current:
            self.transcript_text.insert(tk.END, "\n" + text)
        else:
            self.transcript_text.insert(tk.END, text)
        self.transcript_text.see(tk.END)
    
    def update_partial_transcript(self, text):
        """Update with partial recognition result"""
        current = self.transcript_text.get(1.0, tk.END).strip()
        lines = current.split('\n')
        if lines and lines[-1].endswith("(listening...)"):
            lines[-1] = text + " (listening...)"
        else:
            lines.append(text + " (listening...)")
        self.transcript_text.delete(1.0, tk.END)
        self.transcript_text.insert(tk.END, '\n'.join(lines))
        self.transcript_text.see(tk.END)
    
    def add_subtitle_segment(self, result):
        """Add subtitle segment"""
        if 'text' in result and result['text']:
            # Simple timing estimation
            word_count = len(result['text'].split())
            duration = max(1, word_count * 0.45)  # Rough estimate
            
            # Get last segment end time
            if self.subtitle_segments:
                start_time = self.subtitle_segments[-1]['end']
            else:
                start_time = 0
                
            segment = {
                'start': start_time,
                'end': start_time + duration,
                'text': result['text']
            }
            self.subtitle_segments.append(segment)
            self.update_subtitles()
    
    def update_subtitles(self):
        """Update subtitle text area"""
        self.subtitle_text.delete(1.0, tk.END)
        srt_content = self.build_srt()
        self.subtitle_text.insert(tk.END, srt_content)
        self.subtitle_text.see(tk.END)
    
    def build_srt(self):
        """Build SRT content from subtitle segments"""
        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        srt_lines = []
        for i, segment in enumerate(self.subtitle_segments):
            start_time = format_time(segment['start'])
            end_time = format_time(segment['end'])
            srt_lines.extend([
                str(i + 1),
                f"{start_time} --> {end_time}",
                segment['text'],
                ""
            ])
        
        return "\n".join(srt_lines)
    
    def download_srt(self):
        """Save subtitles as SRT file"""
        if not self.subtitle_segments:
            self.update_status("No subtitles to save")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".srt",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.build_srt())
                self.update_status(f"SRT saved to {filename}")
            except Exception as e:
                self.update_status(f"Error saving SRT: {str(e)}")
    
    def reset_app(self):
        """Reset application state"""
        # Stop any ongoing recording
        if self.is_recording:
            self.stop_recording()
            
        self.audio_file = None
        self.file_label.config(text="No file selected")
        self.transcript_text.delete(1.0, tk.END)
        self.subtitle_text.delete(1.0, tk.END)
        self.subtitle_segments = []
        self.process_btn.config(state=tk.DISABLED)
        self.update_status("Ready")
    
    def update_status(self, message):
        """Update status label"""
        self.status_var.set(message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechRecognitionApp(root)
    root.mainloop()
