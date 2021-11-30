import os

from pathlib import Path

from parsers.DefaultParser import DefaultParser
from parsers.ImageParser import ImageParser
from parsers.PdfParser import PdfParser
from parsers.SheetParser import SheetParser

import streamlit as st

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

    def is_running_on_windows():
        return os.name == 'nt'

    def get_owner():
        try:
            if is_running_on_windows():
                # hack for @st.cache to work properly on macOS
                # because this import tries to get cached 
                # crashing the app on macOS
                from get_file_metadata_windows import get_file_security
                pSD = get_file_security(filepath)
                owner_name, _, _ = pSD.get_owner()
                return owner_name
            else:
                return path_obj.owner()
        except:
            return 'unsupported'

    def get_group():
        try:
            if is_running_on_windows():
                # hack for @st.cache to work properly on macOS
                # because this import tries to get cached 
                # crashing the app on macOS
                from get_file_metadata_windows import get_file_security
                pSD = get_file_security(filepath)
                _, owner_domain, _ = pSD.get_owner()
                return owner_domain
            else:
                return path_obj.group()
        except:
            return 'unsupported'

    return {
        'owner': get_owner(),
        'group': get_group(),
        'size_bytes': stat_info.st_size,
        'last_modified': stat_info.st_mtime,
    }

@st.cache
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
    pii = parser.detect_pii(filepath, file_extension)
    return {
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
            metadata = get_file_metadata(filepath)
            results[filepath]['metadata'] = metadata
        except Exception as e:
            print(f'Error while parsing {filepath}: {e}. Skipping!')

    return results
