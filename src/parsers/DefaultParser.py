import textract

from parsers.detectors.PIIAnalyzerDetector import PIIAnalyzerDetector
from parsers.detectors.PIICatcherDetector import PIICatcherDetector
from parsers.detectors.PresidioDetector import PresidioDetector
from pathlib import Path

from parsers.detectors.DetectorInterface import DetectorInterface

class DefaultParser():
    """
    Default Parser for files

    This class uses textract under the hood to add support to extract
    text from many file types including doc and docx.
    
    To ensure textract works, you need to follow instructions at
    https://textract.readthedocs.io/en/stable/installation.html

    For OSX:
        brew install --cask xquartz
        brew install poppler antiword unrtf tesseract swig
    
    For Ubuntu/Debian:
        apt-get install python-dev libxml2-dev libxslt1-dev antiword \
        unrtf poppler-utils pstotext tesseract-ocr flac ffmpeg lame  \
        libmad0 libsox-fmt-mp3 sox libjpeg-dev swig
    """
    detectors = {
        'presidio': PresidioDetector(),
        'pii_catcher': PIICatcherDetector(),
        'pii_analyzer': PIIAnalyzerDetector(),
    }

    def extract_text(self, path):
        """
        Extract text from path

        Args:
            path (str): file path

        Returns:
            str: string contents of file
        """
        try:
            text_bytes = textract.process(path)
            return text_bytes.decode('utf8')
        except Exception as e:
            return Path(path).read_text()

    def clean_text(self, text):
        """
        Removes whitespace and special characters from text

        Args:
            text (str):

        Returns:
            str:
        """
        text_encode = text.encode(encoding="ascii", errors="ignore")
        text_decode = text_encode.decode()
        # cleaning the text to remove extra whitespace 
        return ' '.join([word for word in text_decode.split()])

    def detect_pii(self, path, extension):
        """
        Run pii detection using all detectors

        Args:
            path (str): file path
            extension (str): file extension

        Returns:
            dict: results
        """
        print('Running parser on', path)
        
        text = self.extract_text(path)
        text = self.clean_text(text)

        results = {}

        for detector_name in self.detectors:
            print('Running', detector_name, 'on', path)
            try:
                detector = self.detectors[detector_name]
                results[detector_name] = detector.extract_pii_from_text(text)
            except Exception as e: 
                print(f'Error while running {detector_name} on {path}: {e}. Skipping!')

        return results
