import os

from pathlib import Path

from parsers.DefaultParser import DefaultParser
from parsers.ImageParser import ImageParser
from parsers.PdfParser import PdfParser
from parsers.SheetParser import SheetParser

default_parser = DefaultParser()
pdf_parser = PdfParser()
image_parser = ImageParser()
sheet_parser = SheetParser()

def list_filepaths(path):
    """
    Yields file paths in folder

    Args:
        path (str): folder path

    Yields:
        Generator[str, None, None]: file path
    """
    for root, dirs, files in os.walk(path):
        for filename in files:
            yield os.path.join(root, filename)
        for dirname in dirs:
            yield os.path.join(root, dirname)

def get_file_extension(filepath):
    """
    Returns file extension from file path

    Args:
        filepath (str): [description]

    Returns:
        str: [description]
    """
    filepath_tup = os.path.splitext(filepath)
    return filepath_tup[1]

def get_parser(file_extension):
    """
    Returns correct parser for file extension

    Args:
        file_extension (str):

    Returns:
        DefaultParser: parser of type DefaultParser or inheriting type DefaultParser
    """
    if file_extension in ['.csv', '.xls', '.xlsx']:
        return sheet_parser
    elif file_extension in ['.pdf']:
        return pdf_parser
    elif file_extension in ['.jpeg', '.png', '.jpg']:
        return image_parser
    else:
        return default_parser

def get_file_metadata(filepath):
    """
    Return user, group, and size metadata

    Args:
        filepath (str):

    Returns:
        dict:
    """
    path_obj = Path(filepath)
    stat_info = os.stat(filepath)
    
    def get_owner():
        try:
            return path_obj.owner()
        except:
            return 'unsupported'

    def get_group():
        try:
            return path_obj.group()
        except:
            return 'unsupported'

    return {
        'owner': get_owner(),
        'group': get_group(),
        'size_bytes': stat_info.st_size,
        'last_modified': stat_info.st_mtime,
    }

def parse_file(filepath, file_extension):
    """
    Parse file using right parser and detect piis

    Args:
        filepath (str):
        file_extension (str):

    Returns:
        dict: results
    """
    parser = get_parser(file_extension)
    metadata = get_file_metadata(filepath)
    pii = parser.detect_pii(filepath, file_extension)
    return {
        'metadata': metadata,
        'pii': pii,
    }

def parse_files(path):
    """
    Helper to run parse_file on every file
    in a folder

    Args:
        path (str): folder path

    Returns:
        dict: results
    """
    results = {}
    for filepath in list_filepaths(path):
        file_extension = get_file_extension(filepath)
        # ignore directories
        if len(file_extension) == 0:
            continue
        try:
            result = parse_file(filepath, file_extension)
            results[filepath] = result
        except Exception as e: 
            print(f'Error while parsing {filepath}: {e}. Skipping!')

    return results
