# AUTOGENERATED! DO NOT EDIT! File to edit: 00r_main.ipynb (unless otherwise specified).

__all__ = ['Session']

# Cell
from typing import List, Tuple, Dict, Optional

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

from .database import Database, Configs
from .stats_refactored import StatisticalTest

# Cell
class Session:

    def __init__(self) -> None:
        self.database = Database()


    def upload_data_via_gui(self, uploader_value: Dict) -> None:
        if list(uploader_value.keys())[0].endswith('.csv'):
            with open("input.csv", "w+b") as i:
                i.write(uploader_value[list(uploader_value.keys())[0]]['content'])
            df = pd.read_csv('input.csv')
        elif list(uploader_value.keys())[0].endswith('.xlsx'):
            with open("input.xlsx", "w+b") as i:
                i.write(uploader_value[list(uploader_value.keys())[0]]['content'])
            df = pd.read_excel('input.xlsx')
        else:
            raise ValueError(f'The file you chose does not correspond to a ".csv" or ".xslx" file! Please restart the GUI and change your selection.')
        if df.columns[0] == 'Unnamed: 0':
            row_wise_differences_excluding_first = df['Unnamed: 0'].diff(1)[1:]
            if (row_wise_differences_excluding_first.unique().shape[0] == 1) and (row_wise_differences_excluding_first.unique()[0] == 1):
                df = df.drop('Unnamed: 0', axis = 1)
        setattr(self.database, 'data', df)


    def upload_data_via_api(self, filepath: Path) -> None:
        if filepath.name.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filepath.name.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            raise ValueError(f'The path you provided ({filepath}) does not correspond to a ".csv" or ".xslx" file!')
        if df.columns[0] == 'Unnamed: 0':
            row_wise_differences_excluding_first = df['Unnamed: 0'].diff(1)[1:]
            if (row_wise_differences_excluding_first.unique().shape[0] == 1) and (row_wise_differences_excluding_first.unique()[0] == 1):
                df = df.drop('Unnamed: 0', axis = 1)
        setattr(self.database, 'data', df)


    def check_for_validity_of_data(self):
        # check if self.database.data matches required criteria
        pass

    def calculate_stats(self, statistical_test: StatisticalTest, show: bool=True, save: bool=False) -> None:
        self.database = statistical_test().compute(database = self.database)
        self.database.plot_handler = statistical_test().plot_handler


    def create_plot(self, filepath: Optional[Path]=None, dpi: Optional[int]=None, show: bool=True, save: bool=False) -> None:
        self.database = self.database.plot_handler().plot(database = self.database)
        if show:
            plt.tight_layout()
            plt.show()
        if save:
            if dpi == None:
                dpi = 300
            if filepath != None:
                plt.tight_layout()
                plt.savefig(filepath, dpi = dpi)
                plt.close()
            else:
                plt.tight_layout()
                plt.savefig('customized_plot.png', dpi = dpi)
                plt.close()


    def export_configs(self, filepath: Path) -> None:
        self.configs.export_configs_to_file(filepath = filepath)


    def load_configs(self, filepath: Path) -> None:
        self.configs.load_configs_from_file(filepath = filepath)


    def export_stats_results(self, filepath: Optional[Path]=None) -> None:
        self.database.export_stats_results(filepath = filepath)
