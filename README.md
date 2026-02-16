# Audio Speech Recognition Web App

This web-based application allows you to upload an audio file and extract the spoken text using Vosk speech recognition engine. It also provides a microphone interface for live speech recognition.

## Features

- **Audio File Upload:** Select and upload your audio file (MP3, WAV, OGG, etc.) for speech recognition.
- **Language Support:** Recognizes speech in multiple languages including English, Spanish, Portuguese.
- **Microphone Interface:** Use the microphone to start real-time speech recognition.
- **Transcript Display:** Displays the recognized text in a scrollable area below the controls.
- **Audio Preview:** Optionally preview your audio file before processing.
- **SRT File Download:** Export the recognized transcript as an SRT file for use in video editing, subtitling, and other applications.

## How to Use

1. **Upload Audio File:**
   - Click on "Upload Audio File" or drag & drop your audio file into the designated area.
   - Select a language from the dropdown menu.

2. **Load Model:**
   - Click on "Load Model" to load the selected language model.

3. **Process Audio:**
   - Click on "Process Audio" to start speech recognition.
   - Wait for the process to complete and the recognized text will appear in the textarea below.

4. **Verify Recognition:**
   - Optionally, play the audio file using the player controls to verify the accuracy of the recognition.

5. **Reset:**
   - Click on "Reset" to start over with a new file or language model.

## Requirements

- A modern web browser that supports Web Speech API and Web Audio API.
- Ensure you have the Vosk engine installed and accessible in your environment (refer to Vosk documentation for setup instructions).

## Usage Instructions

### Basic Setup

1. Download this HTML file and any dependencies.
2. Place the HTML file in a directory of your choice.
3. Open the HTML file in a web browser.

### Advanced Configuration

- **Customizing Languages:** You can add or modify language support by updating the `modelMap` object in the JavaScript code to include additional languages and their corresponding Vosk model URLs.

```javascript
const modelMap = {
    en: { url: './vosk-model-small-en-us-0.15.tar.gz', name: 'English', id: 'vosk-model-small-en-us-0.15' },
    es: { url: './vosk-model-small-es-0.42.tar.gz', name: 'Spanish', id: 'vosk-model-small-es-0.42' },
    pt: { url: './vosk-model-small-pt-0.3.tar.gz', name: 'Portuguese', id: 'vosk-model-small-pt-0.3' }
};
```

- **Model Files:** Ensure that the Vosk model files (`*.tar.gz`) are accessible and properly configured in your environment.

## Troubleshooting

- If you encounter issues loading the Vosk engine or models, check the console for errors.
- Ensure your browser has permissions to access the microphone if using the real-time recognition feature.
- Verify that your audio file format is supported (MP3, WAV, OGG).

This application provides a convenient and efficient way to perform speech-to-text conversion using Vosk, making it useful for various applications such as transcription, language learning, and more.