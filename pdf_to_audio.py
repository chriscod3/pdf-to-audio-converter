import os
import sys
import argparse
import logging
from PyPDF2 import PdfReader
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile
from pydub import AudioSegment
import multiprocessing
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def pdf_to_audio(input_file, output_file, language='en'):
    try:
        logger.debug(f"Starting conversion of {input_file}")
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_audio_files = []

            # Create progress bar for page processing
            with tqdm(total=total_pages, desc=f"Converting {os.path.basename(input_file)}", 
                     unit="page", leave=False) as pbar:
                
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    
                    if text.strip():  # Only process non-empty pages
                        temp_audio_file = os.path.join(temp_dir, f"page_{i+1}.mp3")
                        tts = gTTS(text=text, lang=language)
                        tts.save(temp_audio_file)
                        temp_audio_files.append(temp_audio_file)
                    
                    pbar.update(1)

            if temp_audio_files:
                combined = AudioSegment.empty()
                with tqdm(total=len(temp_audio_files), desc="Combining audio files", 
                         unit="file", leave=False) as pbar:
                    for temp_file in temp_audio_files:
                        combined += AudioSegment.from_mp3(temp_file)
                        pbar.update(1)
                
                combined.export(output_file, format="mp3")
                logger.debug(f"Successfully converted {input_file} to {output_file}")
                return True
            else:
                logger.warning(f"No text content found in {input_file}")
                return False

    except Exception as e:
        logger.error(f"Error processing {input_file}: {str(e)}", exc_info=True)
        return False

def process_pdf(args):
    input_file, output_file, language = args
    return pdf_to_audio(input_file, output_file, language)

def cleanup_output_folder(output_folder):
    try:
        files = os.listdir(output_folder)
        if files:
            with tqdm(total=len(files), desc="Cleaning output folder", 
                     unit="file", leave=False) as pbar:
                for filename in files:
                    file_path = os.path.join(output_folder, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    pbar.update(1)
            logger.debug(f"Cleaned up output folder: {output_folder}")
    except Exception as e:
        logger.error(f"Error cleaning up output folder {output_folder}: {str(e)}", exc_info=True)

def list_languages():
    try:
        languages = tts_langs()
        print("\nAvailable languages:")
        fmt = "{:<10} {:<30}"
        print(fmt.format("Code", "Language"))
        print("-" * 40)
        for code, name in languages.items():
            print(fmt.format(code, name))
    except Exception as e:
        logger.error(f"Error listing languages: {str(e)}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="Convert PDF files to audio (MP3).")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", "--input", help="Input folder containing PDF files")
    group.add_argument("-f", "--file", help="Single PDF file to convert")
    parser.add_argument("-o", "--output", help="Output folder for audio files (default: output)")
    parser.add_argument("-l", "--language", default="en",
                        help="Language for text-to-speech (default: en)")
    parser.add_argument("--clean", action="store_true", help="Clean the output folder before processing")
    parser.add_argument("--list-languages", action="store_true", help="List all available languages")
    parser.add_argument("-j", "--jobs", type=int, default=multiprocessing.cpu_count(),
                        help="Number of parallel jobs (default: number of CPU cores)")
    parser.add_argument("--log", default="info",
                        choices=["debug", "info", "warning", "error", "critical"],
                        help="Set the logging level (default: info)")

    args = parser.parse_args()

    # Set logging level based on user input
    logging.getLogger().setLevel(getattr(logging, args.log.upper()))

    if args.list_languages:
        list_languages()
        sys.exit(0)

    # Handle single file conversion
    if args.file:
        if not os.path.isfile(args.file):
            logger.error(f"Error: Input file '{args.file}' does not exist.")
            sys.exit(1)
        if not args.file.lower().endswith('.pdf'):
            logger.error(f"Error: Input file '{args.file}' is not a PDF file.")
            sys.exit(1)
            
        # Set default output folder if not specified
        output_folder = args.output or "output"
        os.makedirs(output_folder, exist_ok=True)
        
        output_file = os.path.join(output_folder, 
                                 f"{os.path.splitext(os.path.basename(args.file))[0]}.mp3")
        
        if pdf_to_audio(args.file, output_file, args.language):
            logger.info(f"\nConversion complete. Audio saved as {output_file}")
        else:
            logger.error("Conversion failed.")
        sys.exit(0)

    # Handle folder conversion
    input_folder = args.input or "input"
    output_folder = args.output or "output"

    # Create input and output directories if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # Clean output folder if requested
    if args.clean:
        cleanup_output_folder(output_folder)

    # Check if there are PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    if not pdf_files:
        logger.warning(f"No PDF files found in the '{input_folder}' folder. Please add PDF files to begin conversion.")
        sys.exit(1)

    # Prepare arguments for parallel processing
    process_args = []
    for filename in pdf_files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.mp3")
        process_args.append((input_path, output_path, args.language))

    # Process PDFs in parallel with overall progress bar
    logger.info(f"Starting conversion of {len(pdf_files)} PDFs using {args.jobs} parallel jobs")
    
    with multiprocessing.Pool(args.jobs) as pool:
        results = list(tqdm(
            pool.imap(process_pdf, process_args),
            total=len(process_args),
            desc="Overall progress",
            unit="file"
        ))

    # Print summary
    successful = sum(results)
    logger.info(f"\nConversion complete. {successful} out of {len(pdf_files)} files converted successfully.")

if __name__ == "__main__":
    main()