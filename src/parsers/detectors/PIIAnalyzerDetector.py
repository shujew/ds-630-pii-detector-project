import csv
import pandas as pd
import tempfile
import sys

from commonregex import CommonRegex
from nltk.tag.stanford import StanfordNERTagger

from parsers.detectors.DetectorInterface import DetectorInterface

# to analyze big fields
csv.field_size_limit(min(sys.maxsize, 2147483646))

class PIIAnalyzerDetector(DetectorInterface):
    """
    Detector for PIIAnalyzer
    """

    def extract_pii_from_text(self, text):
        with tempfile.NamedTemporaryFile() as tmp:
            with open(tmp.name, 'w') as f:
                f.write(text)
            piianalyzer = PiiAnalyzer(tmp.name)
            return piianalyzer.analysis()

    def extract_pii_from_df(self, df):
        with tempfile.NamedTemporaryFile() as tmp:
            df.to_csv(tmp)
            piianalyzer = PiiAnalyzer(tmp.name)
            return piianalyzer.analysis()

class PiiAnalyzer(object):
    """
    This code was copied from piianalyzer instead of importing it directly because there were bugs 
    in the library and it wouldn't work on python 3.7
    Adapted from https://gitlab.math.ubc.ca/tomyerex/piianalyzer/-/blob/master/piianalyzer/analyzer.py
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.parser = CommonRegex()
        # change 2: i changed the filepaths down here to reflect the installation path in colab
        self.standford_ner = StanfordNERTagger(
            'stanford-ner-2020-11-17/classifiers/english.conll.4class.distsim.crf.ser.gz',
            'stanford-ner-2020-11-17/stanford-ner.jar'
        )

    def analysis(self):
        people = []
        organizations = []
        locations = []
        emails = []
        phone_numbers = []
        street_addresses = []
        credit_cards = []
        ips = []
        data = []

        with open(self.filepath, 'rU') as filedata:
            reader = csv.reader(filedata)

            for row in reader:
                data.extend(row)
                for text in row:
                    emails.extend(self.parser.emails(text))
                    phone_numbers.extend(self.parser.phones("".join(text.split())))
                    street_addresses.extend(self.parser.street_addresses(text))
                    credit_cards.extend(self.parser.credit_cards(text))
                    ips.extend(self.parser.ips(text))

        for title, tag in self.standford_ner.tag(set(data)):
            if tag == 'PERSON':
                people.append(title)
            if tag == 'LOCATION':
                locations.append(title)
            if tag == 'ORGANIZATION':
                organizations.append(title)

        return {
            'PERSON': people, 
            'LOCATION': locations, 
            'ORGANIZATION': organizations,
            'EMAIL_ADDRESS': emails, 
            'PHONE_NUMBER': phone_numbers, 
            'LOCATION': street_addresses,
            'CREDIT_CARD': credit_cards, 
            'IP_ADDRESS': ips
        }