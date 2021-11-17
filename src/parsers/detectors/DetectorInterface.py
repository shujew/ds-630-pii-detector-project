import pandas as pd


class DetectorInterface():
    """
    Interface used by other dectector classes
    """

    def extract_pii_from_text(self, text):
        """
        Returns pii dictionary for text string

        Args:
            text (str): string to be analyzed

        Returns:
            dict: pii
        """
        pass

    def extract_pii_from_df(self, df):
        """
        Returns pii dictionary for pandas dataframe

        Args:
            df (pd.DataFrame): dataframe to be analyzed

        Returns:
            pd.DataFrame: dataframe with pii filled in
        """
        pass
