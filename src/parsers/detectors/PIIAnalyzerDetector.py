import csv
import os
import pandas as pd
import tempfile
import sys

from commonregex import CommonRegex
from nltk.tag.stanford import StanfordNERTagger

from parsers.detectors.DetectorInterface import DetectorInterface

import streamlit as st

# to analyze big fields
csv.field_size_limit(min(sys.maxsize, 2147483646))


class PIIAnalyzerDetector(DetectorInterface):
    """
    Detector for PIIAnalyzer
    """
    @st.cache
    def extract_pii_from_text(self, text):
        piianalyzer = PiiAnalyzer(text)
        return piianalyzer.text_analysis()
    
    @st.cache
    def extract_pii_from_df(self, df):
        return self.extract_pii_from_text(df.to_string())

class PiiAnalyzer(object):
    """
    This code was copied from piianalyzer instead of importing it directly because there were bugs 
    in the library and it wouldn't work on python 3.7
    Adapted from https://gitlab.math.ubc.ca/tomyerex/piianalyzer/-/blob/master/piianalyzer/analyzer.py
    """
    def __init__(self, text):
        self.text = text
        self.parser = CommonRegex()
        # change 2: i changed the filepaths down here to reflect the installation path in colab
        self.standford_ner = StanfordNERTagger(
            'stanford-ner-2020-11-17/classifiers/english.conll.4class.distsim.crf.ser.gz',
            'stanford-ner-2020-11-17/stanford-ner.jar'
        )

    def text_analysis(self):
        people = []
        organizations = []
        locations = []
        emails = []
        phone_numbers = []
        street_addresses = []
        credit_cards = []
        ips = []
        data = []

        # using regex
        emails.extend(self.parser.emails(self.text))
        phone_numbers.extend(self.parser.phones("".join(self.text.split())))
        street_addresses.extend(self.parser.street_addresses(self.text))
        credit_cards.extend(self.parser.credit_cards(self.text))
        ips.extend(self.parser.ips(self.text))

        # using stanford ner
        data = self.text.split()
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
