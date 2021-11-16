import pandas as pd

from parsers.DefaultParser import DefaultParser

class SheetParser(DefaultParser):
    """
    Adds supports for detecting PII from excel files
    """

    def load_csv(self, path):
        """
        Loads csv file into dataframe

        Args:
            path (str): filepath

        Returns:
            pd.DataFrame:
        """
        return pd.read_csv(path)

    def load_excel(self, path):
        """
        Loads excel file into dataframe

        Args:
            path (str): filepath

        Returns:
            pd.DataFrame:
        """
        return pd.DataFrame(pd.read_excel(path))

    def detect_pii(self, path, extension):
        print('Running sheet parser on', path)

        if extension == '.csv':
            df = self.load_csv(path)
        else:
            df = self.load_excel(path)
        
        results = {}

        for detector_name in self.detectors:
            print('Running', detector_name, 'on', path)
            try:
                detector = self.detectors[detector_name]
                results[detector_name] = detector.extract_pii_from_df(df)
            except Exception as e: 
                print(f'Error while running {detector_name} on {path}: {e}. Skipping!')

        return results
