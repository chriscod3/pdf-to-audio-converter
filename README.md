# PDF to Audio Converter

A Python script that converts PDF files to MP3 audio 
files using Google Text-to-Speech (gTTS). The script 
can process both single PDF files and entire 
directories of PDFs.

## Features

- Convert single PDF files or entire directories to 
MP3 audio
- Support for multiple languages (using Google 
Text-to-Speech)
- Progress bars for real-time conversion tracking
- Parallel processing for faster conversion of 
multiple files
- Error handling and logging
- Clean and simple command-line interface

## Prerequisites

- Python 3.x
- FFmpeg (required for audio processing)

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd pdf-to-audio-converter
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install required dependencies:
```bash
pip install PyPDF2 gtts pydub tqdm
```

4. Install FFmpeg:
- Windows: Download from [FFmpeg 
website](https://ffmpeg.org/download.html)
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

## Usage

### Converting a Single File
```bash
python pdf_to_audio.py -f path/to/your/file.pdf
```

### Converting All PDFs in a Directory
```bash
python pdf_to_audio.py -i input_folder
```

### Additional Options
```bash
# List available languages
python pdf_to_audio.py --list-languages

# Convert using a specific language (e.g., French)
python pdf_to_audio.py -f file.pdf -l fr

# Specify output directory
python pdf_to_audio.py -f file.pdf -o output_folder

# Clean output directory before processing
python pdf_to_audio.py -i input_folder --clean

# Set logging level
python pdf_to_audio.py -f file.pdf --log debug
```

### Command Line Arguments

- `-f, --file`: Single PDF file to convert
- `-i, --input`: Input folder containing PDF files
- `-o, --output`: Output folder for audio files 
(default: output)
- `-l, --language`: Language for text-to-speech 
(default: en)
- `--clean`: Clean output folder before processing
- `--list-languages`: List all available languages
- `-j, --jobs`: Number of parallel jobs (default: 
number of CPU cores)
- `--log`: Set logging level (choices: debug, info, 
warning, error, critical)

## Project Structure
```
pdf-to-audio-converter/
├── venv/
├── input/
├── output/
├── pdf_to_audio.py
└── README.md
```

## Error Handling

The script includes comprehensive error handling for 
common issues:
- Missing input files or directories
- Invalid PDF files
- Text extraction failures
- Audio conversion errors

## License

This project is licensed under the MIT License - see 
the LICENSE file for details.
