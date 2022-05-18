# AUTOGENERATED! DO NOT EDIT! File to edit: 00r_database.ipynb (unless otherwise specified).

__all__ = ['DEFAULT_CONFIGS', 'Configs', 'Database']

# Cell
from typing import List, Tuple, Dict, Optional

import pandas as pd
import numpy as np
import math
from pathlib import Path

# Cell
DEFAULT_CONFIGS = {# General features:
                  'fig_width': 28,
                  'fig_height': 16,
                  'show_legend': True,
                  'marker_size': 5,
                  'color_palette': 'colorblind',
                  'save_plot': False,
                  'boxplot_width': 0.8,
                  'boxplot_linewidth': 1.5,
                  'rm_linewidth': 0.5,
                  'rm_linestyle': 'dashed',
                  'rm_linecolor': 'black',
                  'rm_alpha': 0.8,

                  # Axes of the plot:
                  'axes_linewidth': 1,
                  'axes_color': '#000000',
                  'axes_tick_size': 10,
                  'yaxis_label_text': 'data',
                  'yaxis_label_fontsize': 12,
                  'yaxis_label_color': '#000000',
                  'xaxis_label_text': 'groups',
                  'xaxis_label_fontsize': 12,
                  'xaxis_label_color': '#000000',
                  'yaxis_scaling_mode': 'auto',
                  'yaxis_lower_lim': 0,
                  'yaxis_upper_lim': 1,

                  # Annotations:
                  'distance_brackets_to_data': 0.1,
                  'annotation_brackets_factor': 1,
                  'distance_stars_to_brackets': 0.5,
                  'linewidth_annotations': 1.5,
                  'fontsize_stars': 10,
                  'fontweight_stars': 'bold',
                  'l_stats_to_annotate': [],
                  'l_hue_order': []
                 }

# Cell
class Configs:

    def __init__(self):
        self.update(updates = DEFAULT_CONFIGS)


    def update(self, updates: Dict) -> None:
        for key, value in updates.items():
            setattr(self, key, value)

# Cell
class Database:

    def __init__(self) -> None:
        self.configs = Configs()
        self.undo_configs_version = Configs()
        self.redo_configs_version = Configs()


    def update_configs(self, updates: Dict) -> None:
        self.undo_configs_version = self.configs.copy()
        self.configs.update(updates = updates)
        self.redo_configs_version = self.configs.copy()


    def undo_configs_changes(self) -> None:
        self.configs = self.undo_configs_version.copy()


    def redo_configs_changes(self) -> None:
        self.configs = self.redo_configs_version.copy()


    def export_stats_results(self, filepath: Optional[Path]) -> None:
        if 'all_session_ids' in self.stats_results['df_infos'].keys():
            include_sessions = True
        else:
            include_sessions = False
        if type(self.stats_results['pairwise_comparisons']) == pd.DataFrame:
            include_pairwise_comparisons = True
        else:
            include_pairwise_comparisons = False

        df_individual_group_stats = self._get_individual_group_stats_for_download(include_sessions = include_sessions)
        df_group_level_overview = self._get_group_level_stats_for_download()

        if include_pairwise_comparisons:
            df_pairwise_comparisons = self.stats_results['pairwise_comparisons'].copy()

        if filepath == None:
            filepath = 'statistic_results.xlsx'
        with pd.ExcelWriter(filepath) as writer:
            df_individual_group_stats.to_excel(writer, sheet_name='Individual group statistics')
            df_group_level_overview.to_excel(writer, sheet_name='Whole-group statistics')
            if include_pairwise_comparisons:
                df_pairwise_comparisons.to_excel(writer, sheet_name='Pairwise comparisons')



    def _get_individual_group_stats_for_download(self, include_sessions: bool) -> pd.DataFrame:
        d_individual_group_stats = {'means': [],
                                    'medians': [],
                                    'stddevs': [],
                                    'stderrs': [],
                                    'tests': [],
                                    'test_stats': [],
                                    'pvals': [],
                                    'bools': []}
        l_for_index = []
        if include_sessions == False:
            # for independent samples & one sample:
            for group_id in self.stats_results['df_infos']['all_group_ids']:
                d_individual_group_stats = self._calculate_individual_group_stats(d_individual_group_stats, group_id)
                l_for_index.append(group_id)
            l_index = l_for_index
        else:
            # for mma:
            for group_id in self.stats_results['df_infos']['all_group_ids']:
                for session_id in self.stats_results['df_infos']['all_session_ids']:
                    d_individual_group_stats = self._calculate_individual_group_stats(d_individual_group_stats, (group_id, session_id))
                    l_for_index.append((group_id, session_id))
                l_index = pd.MultiIndex.from_tuples(l_for_index)
        df_individual_group_stats = pd.DataFrame(data=d_individual_group_stats)
        multi_index_columns = pd.MultiIndex.from_tuples([('Group statistics', 'Mean'), ('Group statistics', 'Median'), ('Group statistics', 'Standard deviation'), ('Group statistics', 'Standard error'),
                                                 ('Test for normal distribution', 'Test'), ('Test for normal distribution', 'Test statistic'), ('Test for normal distribution', 'p-value'),
                                                 ('Test for normal distribution', 'Normally distributed?')])
        df_individual_group_stats.columns = multi_index_columns
        df_individual_group_stats.index = l_index
        return df_individual_group_stats


    def _calculate_individual_group_stats(self, d, key):
        group_data = self.stats_results['group_level_stats'][key]['data']
        d['means'].append(np.mean(group_data))
        d['medians'].append(np.median(group_data))
        d['stddevs'].append(np.std(group_data))
        d['stderrs'].append(np.std(group_data) / math.sqrt(group_data.shape[0]))
        d['tests'].append('Shapiro-Wilk')
        d['test_stats'].append(self.stats_results['group_level_stats'][key]['normality_test_results'].iloc[0,0])
        d['pvals'].append(self.stats_results['group_level_stats'][key]['normality_test_results'].iloc[0,1])
        d['bools'].append(self.stats_results['group_level_stats'][key]['is_normally_distributed'])
        return d


    def _get_group_level_stats_for_download(self):
        if len(self.stats_results['df_infos']['all_group_ids']) > 1:
            df_group_level_overview = self.stats_results['summary_stats']['homoscedasticity_test_results'].copy()
            df_group_level_overview.index = [0]
            df_group_level_overview.columns = pd.MultiIndex.from_tuples([('Levene', 'W statistic'), ('Levene', 'p value'), ('Levene', 'Equal variances?')])
            df_group_level_overview[('', 'all normally distributed?')] = self.stats_results['summary_stats']['all_normally_distributed']
            df_group_level_overview[('', 'critera for parametric test fulfilled?')] = self.stats_results['summary_stats']['use_parametric']
            df_group_level_overview[('', 'performed test')] = self.stats_results['summary_stats']['performed_test']
        else:
            group_level_overview = dict()
            group_level_overview[('general information', 'all normally distributed?')] = self.stats_results['summary_stats']['all_normally_distributed']
            group_level_overview[('general information', 'critera for parametric test fulfilled?')] = self.stats_results['summary_stats']['use_parametric']
            group_level_overview[('general information', 'performed test')] = self.stats_results['summary_stats']['performed_test']
            df_group_level_overview = pd.DataFrame(data = group_level_overview, index=[0])
        df_group_level_overview[' '] = ''
        df_group_statistics = self.stats_results['summary_stats']['full_test_results'].copy()
        df_group_statistics.index = list(range(df_group_statistics.shape[0]))
        df_group_statistics.columns = pd.MultiIndex.from_tuples([(self.stats_results['summary_stats']['performed_test'], elem) for elem in df_group_statistics.columns])
        df_group_level_overview = pd.concat([df_group_level_overview, df_group_statistics], axis=1)
        return df_group_level_overview