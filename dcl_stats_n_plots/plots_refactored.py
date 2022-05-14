# AUTOGENERATED! DO NOT EDIT! File to edit: 00r_plots.ipynb (unless otherwise specified).

__all__ = ['sort_by_third', 'PlotHandler', 'OneSamplePlots', 'MultipleIndependentSamplesPlots', 'MixedModelANOVAPlots']

# Cell
from typing import Tuple, Dict, List, Optional, Union
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from .database import Database

# Cell
def sort_by_third(e):
    return e[3]

# Cell
class PlotHandler(ABC):

    @property
    @abstractmethod
    def plot_options_displayed_in_gui(self) -> List[str]:
        pass


    @abstractmethod
    def add_handler_specific_plots(self) -> Tuple[plt.Figure, plt.Axes]:
        fig = self.fig
        ax = self.ax
        # do whatever
        return fig, ax


    @abstractmethod
    def add_handler_specific_stats_annotations(self) -> Tuple[plt.Figure, plt.Axes]:
        fig = self.fig
        ax = self.ax
        # do whatever
        return fig, ax


    def plot(self, database: Database) -> Database:
        self.database = database
        self.configs = database.configs
        self.data = database.data.copy()
        self.stats_results = database.stats_results.copy()
        self.fig, self.ax = self.initialize_plot()
        self.fig, self.ax = self.add_handler_specific_plots()
        self.fig, self.ax = self.add_handler_specific_stats_annotations()
        self.fig, self.ax = self.finish_plot()
        database.created_plot = self
        return database


    def initialize_plot(self) -> Tuple[plt.Figure, plt.Axes]:
        fig = plt.figure(figsize=(self.configs.fig_width/2.54 , self.configs.fig_height/2.54), facecolor='white')
        ax = fig.add_subplot()
        for axis in ['top', 'right']:
            ax.spines[axis].set_visible(False)
        for axis in ['bottom','left']:
            ax.spines[axis].set_linewidth(self.configs.axes_linewidth)
            ax.spines[axis].set_color(self.configs.axes_color)
        ax.tick_params(labelsize=self.configs.axes_tick_size, colors=self.configs.axes_color)
        return fig, ax


    def finish_plot(self) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = self.fig, self.ax
        yaxis_label = self.add_linebreaks_to_axis_labels(user_input = self.configs.yaxis_label_text)
        xaxis_label = self.add_linebreaks_to_axis_labels(user_input = self.configs.xaxis_label_text)
        ax.set_ylabel(yaxis_label, fontsize=self.configs.yaxis_label_fontsize, color=self.configs.yaxis_label_color)
        ax.set_xlabel(xaxis_label, fontsize=self.configs.xaxis_label_fontsize, color=self.configs.xaxis_label_color)
        if self.configs.yaxis_scaling_mode == 'manual': #1 for GUI, manual for API
            ax.set_ylim([self.configs.yaxis_lower_lim,self.configs.yaxis_upper_lim])
        return fig, ax


    def add_linebreaks_to_axis_labels(self, user_input: str) -> str:
        all_lines = []
        while '\\' in user_input:
            all_lines.append(user_input[:user_input.find('\\n')-1])
            user_input = user_input.replace(user_input[:user_input.find('\\n')+3], '')
        all_lines.append(user_input)
        for line_index in range(len(all_lines)):
            if line_index == 0:
                label_to_set = all_lines[line_index]
            else:
                label_to_set += f'\n{all_lines[line_index]}'
        return label_to_set


    def get_stars_str(self, df_tmp: pd.DataFrame, group1: str, group2: str) -> str:
        if df_tmp.loc[(df_tmp['A'] == group1) & (df_tmp['B'] == group2)].shape[0] > 0:
            if 'p-corr' in df_tmp.loc[(df_tmp['A'] == group1) & (df_tmp['B'] == group2)].columns:
                pval = df_tmp.loc[(df_tmp['A'] == group1) & (df_tmp['B'] == group2), 'p-corr'].iloc[0]
            else:
                pval = df_tmp.loc[(df_tmp['A'] == group1) & (df_tmp['B'] == group2), 'p-unc'].iloc[0]

        elif df_tmp.loc[(df_tmp['B'] == group1) & (df_tmp['A'] == group2)].shape[0] > 0:
            if 'p-corr' in df_tmp.loc[(df_tmp['B'] == group1) & (df_tmp['A'] == group2)].columns:
                pval = df_tmp.loc[(df_tmp['B'] == group1) & (df_tmp['A'] == group2), 'p-corr'].iloc[0]
            else:
                pval = df_tmp.loc[(df_tmp['B'] == group1) & (df_tmp['A'] == group2), 'p-unc'].iloc[0]
        else:
            print('There was an error with annotating the stats!')
        if pval <= 0.001:
            stars = '***'
        elif pval <= 0.01:
            stars = '**'
        elif pval <= 0.05:
            stars = '*'
        else:
            stars = 'n.s.'
        return stars

# Cell
class OneSamplePlots(PlotHandler):

    @property
    def plot_options_displayed_in_gui(self) -> List[str]:
        return ['stripplot', 'boxplot', 'boxplot with stripplot overlay', 'violinplot', 'violinplot with stripplot overlay']


    def add_handler_specific_plots(self) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = self.fig, self.ax
        data_column_name = self.database.stats_results['df_infos']['data_column_name']
        group_column_name = self.database.stats_results['df_infos']['group_column_name']
        fixed_value = self.database.stats_results['df_infos']['fixed_value']
        if self.configs.plot_type == 'stripplot':
            sns.stripplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          palette = self.configs.color_palette, size = self.configs.marker_size, ax=ax)
            ax.hlines(y = fixed_value, xmin = -0.5, xmax = 0.5, color = 'gray', linestyle = 'dashed')
        elif self.configs.plot_type == 'boxplot':
            sns.boxplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                        palette = self.configs.color_palette, ax=ax)
            ax.hlines(y = fixed_value, xmin = -0.5, xmax = 0.5, color = 'gray', linestyle = 'dashed')
        elif self.configs.plot_type == 'boxplot with stripplot overlay':
            sns.boxplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                        palette = self.configs.color_palette, ax=ax, showfliers=False)
            sns.stripplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          color = 'k', size = self.configs.marker_size, ax=ax)
            ax.hlines(y = fixed_value, xmin = -0.5, xmax = 0.5, color = 'gray', linestyle = 'dashed')
        elif self.configs.plot_type == 'violinplot':
            sns.violinplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                           palette = self.configs.color_palette, cut=0, ax=ax)
            ax.hlines(y = fixed_value, xmin = -0.5, xmax = 0.5, color = 'gray', linestyle = 'dashed')
        elif self.configs.plot_type == 'violinplot with stripplot overlay':
            sns.violinplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                           palette = self.configs.color_palette, cut=0, ax=ax)
            sns.stripplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          color = 'k', size = self.configs.marker_size, ax=ax)
            ax.hlines(y = fixed_value, xmin = -0.5, xmax = 0.5, color = 'gray', linestyle = 'dashed')
        return fig, ax


    def add_handler_specific_stats_annotations(self) -> Tuple[plt.Figure, plt.Axes]:
        fig = self.fig
        ax = self.ax
        df = self.data
        if len(self.configs.l_stats_to_annotate) > 0:
            max_total = self.data[self.database.stats_results['df_infos']['data_column_name']].max()
            y_shift_annotation_line = max_total * self.configs.distance_brackets_to_data
            y_shift_annotation_text = y_shift_annotation_line*0.5*self.configs.distance_stars_to_brackets
            y = max_total + y_shift_annotation_line
            ax.text(0, y+y_shift_annotation_text, self.database.stats_results['summary_stats']['stars_str'],
                    ha='center', va='bottom', color='k', fontsize=self.configs.fontsize_stars, fontweight=self.configs.fontweight_stars)
        return fig, ax

# Cell
class MultipleIndependentSamplesPlots(PlotHandler):

    @property
    def plot_options_displayed_in_gui(self) -> List[str]:
        return ['stripplot', 'boxplot', 'boxplot with stripplot overlay', 'violinplot', 'violinplot with stripplot overlay']


    def add_handler_specific_plots(self) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = self.fig, self.ax
        data_column_name = self.database.stats_results['df_infos']['data_column_name']
        group_column_name = self.database.stats_results['df_infos']['group_column_name']
        if self.configs.plot_type == 'stripplot':
            sns.stripplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          palette = self.configs.color_palette, size = self.configs.marker_size, ax=ax)
        elif self.configs.plot_type == 'boxplot':
            sns.boxplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                        palette = self.configs.color_palette, ax=ax)
        elif self.configs.plot_type == 'boxplot with stripplot overlay':
            sns.boxplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                        palette = self.configs.color_palette, ax=ax, showfliers=False)
            sns.stripplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          color = 'k', size = self.configs.marker_size, ax=ax)
        elif self.configs.plot_type == 'violinplot':
            sns.violinplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                           palette = self.configs.color_palette, cut=0, ax=ax)
        elif self.configs.plot_type == 'violinplot with stripplot overlay':
            sns.violinplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                           palette = self.configs.color_palette, cut=0, ax=ax)
            sns.stripplot(data = self.data, x = group_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          color = 'k', size = self.configs.marker_size, ax=ax)
        return fig, ax


    def add_handler_specific_stats_annotations(self) -> Tuple[plt.Figure, plt.Axes]:
        fig = self.fig
        ax = self.ax
        df = self.data
        if len(self.configs.l_stats_to_annotate) > 0:
            max_total = self.data[self.database.stats_results['df_infos']['data_column_name']].max()
            y_shift_annotation_line = max_total * self.configs.distance_brackets_to_data
            brackets_height = y_shift_annotation_line*0.5*self.configs.annotation_brackets_factor
            y_shift_annotation_text = brackets_height + y_shift_annotation_line*0.5*self.configs.distance_stars_to_brackets
            y = max_total + y_shift_annotation_line
            df_temp = self.database.stats_results['pairwise_comparisons'].copy()
            for group1, group2 in self.configs.l_stats_to_annotate:
                x1 = self.configs.l_xlabel_order.index(group1)
                x2 = self.configs.l_xlabel_order.index(group2)
                stars = self.get_stars_str(df_temp, group1, group2)
                ax.plot([x1, x1, x2, x2], [y, y+brackets_height, y+brackets_height, y], c='k', lw=self.configs.linewidth_annotations)
                ax.text((x1+x2)*.5, y+y_shift_annotation_text, stars, ha='center', va='bottom', color='k',
                         fontsize=self.configs.fontsize_stars, fontweight=self.configs.fontweight_stars)
                # With set_distance_stars_to_brackets being limited to 5, stars will always be closer than next annotation line
                y = y+3*y_shift_annotation_line
        return fig, ax

# Cell
class MixedModelANOVAPlots(PlotHandler):

    @property
    def plot_options_displayed_in_gui(self) -> List[str]:
        return ['pointplot', 'boxplot', 'boxplot with stripplot overlay', 'violinplot', 'violinplot with stripplot overlay']


    def add_handler_specific_plots(self) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = self.fig, self.ax
        data_column_name = self.database.stats_results['df_infos']['data_column_name']
        group_column_name = self.database.stats_results['df_infos']['group_column_name']
        session_column_name = self.database.stats_results['df_infos']['session_column_name']

        if self.configs.plot_type == 'pointplot':
            sns.pointplot(data = self.data, x = session_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          hue = group_column_name, hue_order = self.configs.l_hue_order, palette = self.configs.color_palette,
                          dodge = True, ci = 'sd', err_style = 'bars', capsize = 0, ax = ax)
        elif self.configs.plot_type == 'boxplot':
            sns.boxplot(data = self.data, x = session_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                        hue = group_column_name, hue_order = self.configs.l_hue_order, palette = self.configs.color_palette, ax = ax)
        elif self.configs.plot_type == 'boxplot with stripplot overlay':
            sns.boxplot(data = self.data, x = session_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                        hue = group_column_name, hue_order = self.configs.l_hue_order, palette = self.configs.color_palette, ax = ax, showfliers = False)
            sns.stripplot(data = self.data, x = session_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          hue = group_column_name, hue_order = self.configs.l_hue_order, dodge = True, color = 'k', size = self.configs.marker_size)
        elif self.configs.plot_type == 'violinplot':
            sns.violinplot(data = self.data, x = session_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                           hue = group_column_name, hue_order = self.configs.l_hue_order, palette = self.configs.color_palette,
                           width = 0.8, cut = 0, ax = ax)
        elif self.configs.plot_type == 'violinplot with stripplot overlay':
            sns.violinplot(data = self.data, x = session_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                           hue = group_column_name, hue_order = self.configs.l_hue_order, palette = self.configs.color_palette,
                           width = 0.8, cut = 0, ax = ax)
            sns.stripplot(data = self.data, x = session_column_name, y = data_column_name, order = self.configs.l_xlabel_order,
                          hue = group_column_name, hue_order = self.configs.l_hue_order, dodge = True, color = 'k', size = self.configs.marker_size)
        return fig, ax


    def add_handler_specific_stats_annotations(self) -> Tuple[plt.Figure, plt.Axes]:
        fig = self.fig
        ax = self.ax
        df = self.data
        if len(self.configs.l_stats_to_annotate) > 0:
            if self.configs.plot_type in ['boxplot', 'boxplot with stripplot overlay', 'violinplot', 'violinplot with stripplot overlay']:
                fig, ax = self.annotate_stats_mma()
            elif self.configs.plot_type == 'pointplot':
                fig, ax = self.annotate_stats_mma_pointplot()
        if self.configs.show_legend == True:
            if self.configs.plot_type == 'pointplot':
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
            if self.configs.plot_type in ['boxplot', 'boxplot with stripplot overlay', 'violinplot', 'violinplot with stripplot overlay']:
                handles, labels = ax.get_legend_handles_labels()
                new_handles = handles[:len(self.configs.l_hue_order)]
                new_labels = labels[:len(self.configs.l_hue_order)]
                ax.legend(new_handles, new_labels, loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
        else:
            ax.get_legend().remove()
        return fig, ax


    def annotate_stats_mma(self) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = self.fig, self.ax
        l_stats_to_annotate = self.configs.l_stats_to_annotate
        group_col = self.database.stats_results['df_infos']['group_column_name']
        data_col = self.database.stats_results['df_infos']['data_column_name']
        session_col = self.database.stats_results['df_infos']['session_column_name']
        l_sessions = self.database.stats_results['df_infos']['all_session_ids']
        distance_brackets_to_data = self.configs.distance_brackets_to_data
        annotation_brackets_factor = self.configs.annotation_brackets_factor
        distance_stars_to_brackets = self.configs.distance_stars_to_brackets
        l_xlabel_order = self.configs.l_xlabel_order
        l_hue_order = self.configs.l_hue_order
        df = self.data
        if len(l_stats_to_annotate) > 0:
            l_to_annotate_ordered = []
            for session_id in l_sessions:
                l_temp = [elem for elem in l_stats_to_annotate if elem[2]==session_id]
                for elem in l_temp:
                    abs_mean_difference = abs(df.loc[(df[group_col]==elem[0]) & (df[session_col]==elem[2]), data_col].mean()-
                                              df.loc[(df[group_col]==elem[1]) & (df[session_col]==elem[2]), data_col].mean())
                    l_temp[l_temp.index(elem)] = elem+(abs_mean_difference,)
                l_temp.sort(key=sort_by_third)
                l_to_annotate_ordered = l_to_annotate_ordered+l_temp
            df_temp = self.database.stats_results['pairwise_comparisons'].copy()
            max_total = df[data_col].max()
            y_shift_annotation_line = max_total * distance_brackets_to_data
            brackets_height = y_shift_annotation_line*0.5*annotation_brackets_factor
            y_shift_annotation_text = brackets_height + y_shift_annotation_line*0.5*distance_stars_to_brackets

            for elem in l_to_annotate_ordered:
                group1, group2, session_id, abs_mean_difference = elem

                if l_to_annotate_ordered.index(elem) == 0:
                    n_previous_annotations_in_this_session_id = 0
                elif session_id == prev_session:
                    n_previous_annotations_in_this_session_id = n_previous_annotations_in_this_session_id + 1
                else:
                    n_previous_annotations_in_this_session_id = 0

                y = max_total + y_shift_annotation_line + y_shift_annotation_line*n_previous_annotations_in_this_session_id*3

                width = 0.8
                x_base = l_xlabel_order.index(session_id) - width/2 + width/(2*len(l_hue_order))
                x1 = x_base + width/len(l_hue_order)*l_hue_order.index(group1)
                x2 = x_base + width/len(l_hue_order)*l_hue_order.index(group2)

                stars = self.get_stars_str(df_temp.loc[df_temp[session_col] == session_id], group1, group2)

                ax.plot([x1, x1, x2, x2], [y, y+brackets_height, y+brackets_height, y], color='k', lw=self.configs.linewidth_annotations)
                ax.text((x1+x2)/2, y+y_shift_annotation_text, stars, ha='center', va='bottom',
                         fontsize=self.configs.fontsize_stars, fontweight=self.configs.fontweight_stars)

                prev_session = session_id
        return fig, ax


    def annotate_stats_mma_pointplot(self) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = self.fig, self.ax
        l_stats_to_annotate = self.configs.l_stats_to_annotate
        group_col = self.database.stats_results['df_infos']['group_column_name']
        data_col = self.database.stats_results['df_infos']['data_column_name']
        session_col = self.database.stats_results['df_infos']['session_column_name']
        l_sessions = self.database.stats_results['df_infos']['all_session_ids']
        distance_brackets_to_data = self.configs.distance_brackets_to_data
        annotation_brackets_factor = self.configs.annotation_brackets_factor
        distance_stars_to_brackets = self.configs.distance_stars_to_brackets
        l_xlabel_order = self.configs.l_xlabel_order
        df = self.data
        if len(l_stats_to_annotate) > 0:
            l_to_annotate_ordered = []
            for session_id in l_sessions:
                l_temp = [elem for elem in l_stats_to_annotate if elem[2]==session_id]
                for elem in l_temp:
                    abs_mean_difference = abs(df.loc[(df[group_col]==elem[0]) & (df[session_col]==elem[2]), data_col].mean()-
                                              df.loc[(df[group_col]==elem[1]) & (df[session_col]==elem[2]), data_col].mean())
                    l_temp[l_temp.index(elem)] = elem+(abs_mean_difference,)
                l_temp.sort(key=sort_by_third)
                l_to_annotate_ordered = l_to_annotate_ordered+l_temp
            df_temp = self.database.stats_results['pairwise_comparisons'].copy()
            for elem in l_to_annotate_ordered:
                group1, group2, session_id, abs_mean_difference = elem
                if l_to_annotate_ordered.index(elem) == 0:
                    n_previous_annotations_in_this_session_id = 0
                elif session_id == prev_session:
                    n_previous_annotations_in_this_session_id = n_previous_annotations_in_this_session_id + 1
                else:
                    n_previous_annotations_in_this_session_id = 0
                x_shift_annotation_line = distance_brackets_to_data + distance_brackets_to_data * n_previous_annotations_in_this_session_id * 1.5
                brackets_height = distance_brackets_to_data*0.5*annotation_brackets_factor
                x_shift_annotation_text = brackets_height + distance_brackets_to_data*0.5*distance_stars_to_brackets
                x = l_xlabel_order.index(session_id) + x_shift_annotation_line
                y1=df.loc[(df[group_col] == group1) & (df[session_col] == session_id), data_col].mean()
                y2=df.loc[(df[group_col] == group2) & (df[session_col] == session_id), data_col].mean()
                stars = self.get_stars_str(df_temp.loc[df_temp[session_col] == session_id], group1, group2)
                ax.plot([x, x+brackets_height, x+brackets_height, x], [y1, y1, y2, y2], color='k', lw=self.configs.linewidth_annotations)
                ax.text(x+x_shift_annotation_text, (y1+y2)/2, stars, rotation=-90, ha='center', va='center',
                         fontsize=self.configs.fontsize_stars, fontweight=self.configs.fontweight_stars)
                prev_session = session_id
        return fig, ax