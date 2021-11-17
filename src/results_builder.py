import pandas as pd

# dict converting pii to score value
# scores were assigned arbitrarily based on
# which pii we felt had more risk than others
# e.g. credit card info is worse than first name
pii_name_to_score = {
    'CREDIT_CARD': 1,
    'CRYPTO': 1,
    'DATE_TIME': 0.1,
    'DOMAIN_NAME': 0.1,
    'EMAIL': 0.3,
    'EMAIL_ADDRESS': 0.3,
    'IBAN_CODE': 0.3,
    'IP_ADDRESS': 0.5,
    'NRP': 0.7,
    'ADDRESS': 0.7,
    'LOCATION': 0.7,
    'PERSON': 0.7,
    'PHONE': 0.7,
    'PHONE_NUMBER': 0.7,
    'MEDICAL_LICENSE': 1,
    'US_BANK_NUMBER': 1,
    'US_DRIVER_LICENSE': 1,
    'US_ITIN': 1,
    'US_PASSPORT': 1,
    'SSN': 1,
    'US_SSN': 1,
    'UK_NHS': 1,
    'AU_ABN': 1,
    'AU_ACN': 1,
    'AU_TFN': 1,
    'AU_MEDICARE': 1, 
    'ORGANIZATION': 0.2,
    'NONE': 0,
    'UNSUPPORTED': 0,
    'BIRTH_DATE': 0.7,
    'GENDER': 0.7,
    'NATIONALITY': 0.7,
    'USER_NAME': 0.7,
    'PASSWORD': 1,
}

def calculate_overall_pii_score(result):
    """
    Returns overall pii score of a result using
    dictionary pii_name_to_score

    Args:
        result (dict):

    Returns:
        int: pii score
    """
    score = 0

    if 'presidio' in result['pii']:
        presidio_results = result['pii']['presidio']
        for pii_name in presidio_results:
            if pii_name in pii_name_to_score:
                score += (pii_name_to_score[pii_name] * presidio_results[pii_name]['count'])

    if 'pii_analyzer' in result['pii']:
        pii_analyzer_results = result['pii']['pii_analyzer']
        for pii_name in pii_analyzer_results:
            score += (pii_name_to_score[pii_name] * len(pii_analyzer_results[pii_name]))

    if 'pii_catcher' in result['pii']:
        pii_catcher_results = result['pii']['pii_catcher']
        for pii_name in pii_catcher_results:
            score += (pii_name_to_score[pii_name] * pii_catcher_results[pii_name])

    return score

def build_summary_df_from_results(results):
    """
    Builds summary dataframe from results dict

    Args:
        results (dict):

    Returns:
        pd.DataFrame:
    """
    data = []
    for filepath in results:
        pii_score = calculate_overall_pii_score(results[filepath])
        has_pii = pii_score > 0

        flattened_result = {}

        flattened_result['filepath'] = filepath
        flattened_result['has_pii'] = has_pii
        flattened_result['pii_score'] = pii_score
    
        metadata = results[filepath]['metadata']
        flattened_result['size_bytes'] = metadata['size_bytes']
        flattened_result['owner'] = metadata['owner']
        flattened_result['group'] = metadata['group']

        if 'presidio' in results[filepath]['pii']:
            presidio_results = results[filepath]['pii']['presidio']
            for pii_name in presidio_results:
                # ignoring dataframe for presidio analysis
                if pii_name != 'df_pii':
                    flattened_result[f'p_{pii_name.lower()}'] = presidio_results[pii_name]['count']

        if 'pii_analyzer' in results[filepath]['pii']:
            pii_analyzer_results = results[filepath]['pii']['pii_analyzer']
            for pii_name in pii_analyzer_results:
                flattened_result[f'pa_{pii_name.lower()}'] = len(pii_analyzer_results[pii_name])

        if 'pii_catcher' in results[filepath]['pii']:
            pii_catcher_results = results[filepath]['pii']['pii_catcher']
            for pii_name in pii_catcher_results:
                flattened_result[f'pc_{pii_name.lower()}'] = pii_catcher_results[pii_name]

        data.append(flattened_result)
    
    df = pd.DataFrame(data)
    df.fillna(0, inplace=True)

    return df
