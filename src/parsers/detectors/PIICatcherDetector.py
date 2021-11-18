# Need to run
# pip install piicatcher
# python -m spacy download en_core_web_sm
# brew install libmagic

import os
import pandas as pd
import tempfile

from typing import Any, Dict, Optional, TextIO
from piicatcher.explorer.metadata import NamedObject
from piicatcher.piitypes import PiiTypes
from piicatcher.scanner import NERScanner, RegexScanner
from spacy.lang.en import English

from parsers.detectors.DetectorInterface import DetectorInterface


class PIICatcherDetector(DetectorInterface):
    """
    Detector for PIICatcher
    """

    def extract_pii_from_text(self, text):
        # create and write text to temp file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(str.encode(text, encoding='utf-8'))
        # do analysis
        result_summary = {}
        with open(tmp.name) as d:
            result = self.scan_file_object(d)
            result_summary = self.summarize_scan_file_object_results(result)
        # delete temp file
        tmp.close()
        os.unlink(tmp.name)

        return result_summary

    def extract_pii_from_df(self, df):
        # create and write text to temp file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        df.to_csv(tmp)
        # do analysis
        result_summary = {}
        with open(tmp.name) as d:
            result = self.scan_file_object(d)
            result_summary = self.summarize_scan_file_object_results(result)
        # delete temp file
        tmp.close()
        os.unlink(tmp.name)

        return result_summary

    def summarize_scan_file_object_results(self, results):
        summary = {}
        for result in results:
            summary[result.name] = result.value

        if 'PHONE' in summary:
            summary['PHONE_NUMBER'] = summary.pop('PHONE')
        if 'EMAIL' in summary:
            summary['EMAIL_ADDRESS'] = summary.pop('EMAIL')
        if 'SSN' in summary:
            summary['US_SSN'] = summary.pop('SSN')

        return summary

    # This function was only available in v0.13.0 so
    # I ported it to the latest v0.14.0
    def scan_file_object(self, fd):
        scanner = IO("api file object", fd)
        context = {
            "tokenizer": Tokenizer(),
            "regex": RegexScanner(),
            "ner": NERScanner(),
        }

        scanner.scan(context)
        return scanner.get_pii_types()


class IO(NamedObject):
    def __init__(self, name, fd):
        super(IO, self).__init__(name, (), ())
        self.descriptor = fd

    @property
    def descriptor(self):
        return self._descriptor

    @descriptor.setter
    def descriptor(self, fd):
        self._descriptor = fd

    def scan(self, context):
        tokenizer = context["tokenizer"]
        regex = context["regex"]
        ner = context["ner"]

        data = self._descriptor.read()
        [self._pii.add(pii) for pii in ner.scan(data)]
        tokens = tokenizer.tokenize(data)
        for t in tokens:
            if not t.is_stop:
                [self._pii.add(pii) for pii in regex.scan(t.text)]


class File(IO):
    def __init__(self, name, mime_type):
        super(File, self).__init__(name)
        self._mime_type = mime_type

    def get_mime_type(self):
        return self._mime_type

    def scan(self, context):
        if (
            not self._mime_type.startswith("text/")
            and self._mime_type != "application/csv"
        ):
            self._pii.add(PiiTypes.UNSUPPORTED)
        else:
            with open(self.get_name(), "r") as f:
                self.descriptor = f
                super().scan(context)


class Tokenizer:
    def __init__(self):
        nlp = English()
        # Create a Tokenizer with the default settings for English
        # including punctuation rules and exceptions
        self._tokenizer = nlp.tokenizer

    def tokenize(self, data):
        return self._tokenizer(data)
