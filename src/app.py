import base64
import streamlit as st
import pandas as pd
import os


def scan_directory(path):
    from parse_files import parse_files
    from results_builder import build_summary_df_from_results

    is_directory = os.path.isdir(path)
    if not is_directory:
        return (False, False)
    results = parse_files(path)
    df_summary = build_summary_df_from_results(results)
    return (results, df_summary)


def get_html_for_dataframe(df, filename, label):
    csv = df.to_csv(index=False)
    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a download="{filename}" href="data:file/csv;base64,{b64}" target="_blank">{label}</a>'


st.title('Pii Detector Final Project')
st.write('By Shuaib Jewon and Nishil Asnani')

folder_path = st.text_input('Folder path to scan for PII')
st.image('images/app_header.jpg')

if folder_path:
    results, df_summary = scan_directory(folder_path)

    if results:
        st.success(f'Folder {folder_path} was successfully scanned!')

        # convert filepath in df_summary to file name so it can be displayed
        df = df_summary.copy(deep=True)
        df.insert(0, 'filename', df['filepath'].apply(os.path.basename))
        df.drop(['filepath'], axis=1, inplace=True)

        # show summary
        st.header('Results Summary')
        st.write(
            'Please find a summary of scan results. Detailed results will be available further ahead!')
        st.write('pii_score is an overall score to assess the document\'s pii risk and is relative to other files in directory')
        st.write(
            'Colums starting with **p_** indicate that the pii was detected by the **Presidio** detector')
        st.write(
            'Colums starting with **pc_** indicate that the pii was detected by the **PIICatcher** detector')
        st.write(
            'Colums starting with **pa_** indicate that the pii was detected by the **PIIAnalyzer** detector')

        st.dataframe(df)
        st.markdown(
            get_html_for_dataframe(
                df, 'results.csv', 'Download summary in csv format'),
            unsafe_allow_html=True
        )

        st.header('Detailed Results')
        for filepath in results:
            filename = os.path.basename(filepath)
            st.subheader(filename)

            # summary of file
            st.write(f'**Path**: {filepath}')

            pii_score_list = df.loc[df['filename']
                                    == filename]['pii_score'].tolist()
            if len(pii_score_list) > 0:
                st.write(f'**PII Score**: {pii_score_list[0]:2f}')

            metadata = results[filepath]['metadata']
            st.write(f'**Size**: {metadata["size_bytes"]} bytes')
            st.write(f'**User**: {metadata["owner"]}')
            st.write(f'**Group**: {metadata["group"]}')

            pii = results[filepath]['pii']

            if 'pii_analyzer' in pii:
                piianalyzer_pii = pii['pii_analyzer']
                if st.checkbox('Show PIIAnalyzer Results', key=f'{filepath}_piianalyzer'):
                    for pii_type in piianalyzer_pii:
                        values = piianalyzer_pii[pii_type]
                        count = len(values)
                        if count > 0:
                            st.write(
                                f'#### PIIAnalyzer {pii_type} Results ({count}):')
                            st.write(values)

            if 'pii_catcher' in pii:
                piicatcher_pii = pii['pii_catcher']
                if st.checkbox('Show PIICatcher Results', key=f'{filepath}_piicatcher'):
                    for pii_type in piicatcher_pii:
                        value_count = piicatcher_pii[pii_type]
                        if value_count > 0:
                            st.write(
                                f'PIICatcher {pii_type} count: {value_count}')

            if 'presidio' in pii:
                presidio_pii = pii['presidio']
                if st.checkbox('Show Presidio Results', key=f'{filepath}_presidio'):
                    for pii_type in presidio_pii:
                        if pii_type == 'df_pii':
                            # handle presidio df
                            if st.checkbox('Show dataframe with PII filled in', key=f'{filepath}_presidio_df_pii'):
                                st.dataframe(presidio_pii[pii_type])
                        else:
                            values = presidio_pii[pii_type]['values']
                            count = len(values)
                            if count > 0:
                                st.write(
                                    f'#### Presidio {pii_type} Results ({count}):')
                                st.write(values)
    else:
        st.error(f'Error: {folder_path} does not exist!')
