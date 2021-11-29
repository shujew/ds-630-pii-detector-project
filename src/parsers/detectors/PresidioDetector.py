# Need to run
# pip install presidio-analyzer
# python -m spacy download en_core_web_lg

import pandas as pd

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.recognizer_result import RecognizerResult

from parsers.detectors.DetectorInterface import DetectorInterface

from preshed.maps import PreshMap

import streamlit as st

class PresidioDetector(DetectorInterface):
    """
    Detector for Presidio
    """

    def __init__(self):
        self.analyzer = AnalyzerEngine()

    def get_pii_entities(self):
        return [
            'CREDIT_CARD',
            'CRYPTO',
            'DATE_TIME',
            'DOMAIN_NAME',
            'EMAIL_ADDRESS',
            'IBAN_CODE',
            'IP_ADDRESS',
            'NRP',
            'LOCATION',
            'PERSON',
            'PHONE_NUMBER',
            'MEDICAL_LICENSE',
            'US_BANK_NUMBER',
            'US_DRIVER_LICENSE',
            'US_ITIN',
            'US_PASSPORT',
            'US_SSN',
            'UK_NHS',
            'AU_ABN',
            'AU_ACN',
            'AU_TFN',
            'AU_MEDICARE',
        ]

    @st.cache(hash_funcs={PreshMap: lambda x: 0})
    def extract_pii_from_text(self, text):
        summary = {}
        results = self.analyzer.analyze(
            text=text,
            entities=self.get_pii_entities(),
            language='en',
            score_threshold=0.80
        )
        for result in results:
            if result.entity_type not in summary:
                summary[result.entity_type] = {
                    'count': 0,
                    'values': [],
                }
            summary[result.entity_type]['count'] += 1
            summary[result.entity_type]['values'].append(
                text[result.start:result.end]
            )

        return summary

    @st.cache(hash_funcs={PreshMap: lambda x: 0})
    def extract_pii_from_df(self, df):
        summary = {}

        def analyze_cell(t):
            result_list = self.analyzer.analyze(
                text=str(t),
                entities=self.get_pii_entities(),
                language='en',
            )
            if result_list:
                for result in result_list:
                    if result.entity_type not in summary:
                        summary[result.entity_type] = {
                            'count': 0,
                            'score': result.score,
                            'values': [],
                        }
                    summary[result.entity_type]['count'] += 1
                    summary[result.entity_type]['values'].append(t)

            if len(result_list) == 0:
                return ''

            pii_types = ''
            for result in result_list:
                pii_types += f'{result.entity_type},'

            # remove last comma
            return pii_types[:-1]

        df_pii = df \
            .copy(deep=True) \
            .applymap(analyze_cell)

        summary['df_pii'] = df_pii

        return summary
