from results_builder import build_summary_df_from_results
from parse_files import parse_files
import argparse
import pathlib

parser = argparse.ArgumentParser(
    description='Scan a folder for PII'
)

parser.add_argument(
    'path',
    type=pathlib.Path,
    help='folder path to scan'
)

parser.add_argument(
    'results',
    type=pathlib.Path,
    help='where to place results'
)

args = vars(parser.parse_args())
folder_path = args['path']
results_path = args['results']


raw_results = parse_files(folder_path)
df_results = build_summary_df_from_results(raw_results)

df_results.to_csv(results_path)
