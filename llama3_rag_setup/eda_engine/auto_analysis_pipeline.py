import pandas as pd
import numpy as np
import json

class UniversalEDAPipeline:
    """
    Pipeline EDA semplificata: per ora restituisce solo la describe() del DataFrame come output strutturato (JSON).
    """
    def __init__(self, df):
        self.df = df.copy()

    def run_complete_analysis(self):
        result = {
            'describe': self.df.describe(include='all').fillna('').astype(str).to_dict()
        }
        return json.dumps(result, indent=2, default=str)

    def has_object_features(self):
        """
        Restituisce True se ci sono colonne di tipo object (feature categoriche/testuali), altrimenti False.
        """
        object_cols = self.df.select_dtypes(include=['object']).columns
        return len(object_cols) > 0

    def get_object_value_counts(self):
        """
        Restituisce un dizionario con value_counts() per ogni colonna di tipo object (inclusi i NaN),
        dopo aver convertito eventuali colonne data in datetime.
        Esempio: { 'Test Results': { 'Positive': 10, 'Negative': 5, ... } }
        """
        # Prima converto le colonne data
        self.convert_date_columns()
        # Poi calcolo value_counts solo sulle colonne ancora object
        object_cols = self.df.select_dtypes(include=['object']).columns
        value_counts_dict = {}
        for col in object_cols:
            value_counts_dict[col] = self.df[col].value_counts(dropna=False).to_dict()
        return value_counts_dict

    def convert_date_columns(self):
        """
        Cerca colonne che nel nome contengono 'date' (case-insensitive) e le converte in datetime.
        Modifica il DataFrame in-place. Restituisce la lista delle colonne convertite.
        """
        converted = []
        for col in self.df.columns:
            if 'date' in col.lower():
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    converted.append(col)
                except Exception:
                    pass
        return converted

# Funzione utility per chiamate esterne

def run_eda_analysis(df):
    pipeline = UniversalEDAPipeline(df)
    return pipeline.run_complete_analysis()
