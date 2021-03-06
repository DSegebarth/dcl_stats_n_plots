# AUTOGENERATED! DO NOT EDIT! File to edit: 00_stats.ipynb (unless otherwise specified).

__all__ = ['independent_samples', 'one_sample', 'mixed_model_ANOVA']

# Cell
import pandas as pd
import numpy as np
import pingouin as pg
import itertools

# Cell
def independent_samples(df):
    "Compare two or more independent samples"
    data_col = df.columns[0]
    group_col = df.columns[1]
    l_groups = list(df[group_col].unique())

    d_results = {'data_col': data_col,
                 'group_col': group_col,
                 'l_groups': l_groups}

    for group_id in l_groups:
        d_results[group_id] = {'data': df.loc[df[group_col] == group_id, data_col].values,
                            'normality_full': pg.normality(df.loc[df[group_col] == group_id, data_col].values),
                            'normality_bool': pg.normality(df.loc[df[group_col] == group_id, data_col].values)['normal'][0]}

    d_results['summary'] = {'normality': all([d_results[elem]['normality_bool'] for elem in l_groups]),
                         'homoscedasticity': pg.homoscedasticity([d_results[elem]['data'] for elem in l_groups])['equal_var'][0]}

    parametric = all([d_results['summary']['normality'], d_results['summary']['homoscedasticity']])

    if len(l_groups) > 2:
        if parametric:
            d_results['summary']['group_level_statistic'] = pg.anova(data=df, dv=data_col, between=group_col)
            performed_test = 'One-way ANOVA'
        else:
            d_results['summary']['group_level_statistic'] = pg.kruskal(data=df, dv=data_col, between=group_col)
            performed_test = 'Kruskal-Wallis-ANOVA'
        d_results['performed_test'] = performed_test

    if len(l_groups) > 1:
        d_results['summary']['pairwise_comparisons'] = pg.pairwise_ttests(data=df, dv=data_col, between=group_col, parametric=parametric, padjust='holm')

    else:
        print('Error: The group_id column has to contain at least two different group_ids for this selection.\
        \nDid you mean to perform a one-sample test?')

    return d_results

# Cell
def one_sample(df):
    data_col = df.columns[0]
    group_col = df.columns[1]
    fixed_val_col = df.columns[2]
    fixed_value = df[fixed_val_col].values[0]
    l_groups = list(df[group_col].unique())

    d_results = {'data_col': data_col,
                 'group_col': group_col,
                 'fixed_val_col': fixed_val_col,
                 'fixed_value': fixed_value,
                 'l_groups': l_groups}

    group_id = l_groups[0]
    d_results[group_id] = {'data': df.loc[df[group_col] == group_id, data_col].values,
                        'normality_full': pg.normality(df.loc[df[group_col] == group_id, data_col].values),
                        'normality_bool': pg.normality(df.loc[df[group_col] == group_id, data_col].values)['normal'][0]}
    parametric = d_results[group_id]['normality_bool']

    d_results['summary'] = {'normality_full': pg.normality(df.loc[df[group_col] == group_id, data_col].values),
                         'normality_bool': pg.normality(df.loc[df[group_col] == group_id, data_col].values)['normal'][0]}

    if parametric == True:
        d_results['summary']['pairwise_comparisons'] = pg.ttest(df[data_col].values, fixed_value)
        performed_test = 'one sample t-test'
    else:
        d_results['summary']['pairwise_comparisons'] = pg.wilcoxon(df[data_col].values - fixed_value, correction='auto')
        performed_test = 'one sample wilcoxon rank-sum test'

    d_results['performed_test'] = performed_test

    return d_results

# Cell
def mixed_model_ANOVA(df):
    data_col = df.columns[0]
    group_col = df.columns[1]
    subject_col = df.columns[2]
    session_col = df.columns[3]
    l_groups = list(df[group_col].unique())
    l_sessions = list(df[session_col].unique())

    d_results = {}

    for group_id in l_groups:
        for session_id in l_sessions:
            d_results[group_id, session_id] = {'data': df.loc[(df[group_col] == group_id) & (df[session_col] == session_id), data_col].values,
                                            'mean': df.loc[(df[group_col] == group_id) & (df[session_col] == session_id), data_col].mean(),
                                            'normality_full': pg.normality(df.loc[(df[group_col] == group_id)
                                                                                  & (df[session_col] == session_id), data_col].values),
                                            'normality_bool': pg.normality(df.loc[(df[group_col] == group_id)
                                                                                  & (df[session_col] == session_id), data_col].values)['normal'][0]}

    d_results['summary'] = {}
    d_results['summary'] = {'normality': all([d_results[key]['normality_bool'] for key in d_results.keys() if key != 'summary']),
                         'homoscedasticity': pg.homoscedasticity([d_results[key]['data'] for key in d_results.keys() if key != 'summary'])['equal_var'][0]}

    parametric = all([d_results['summary']['normality'], d_results['summary']['homoscedasticity']])

    d_results['summary']['group_level_statistic'] = pg.mixed_anova(data=df, dv=data_col, within=session_col, subject=subject_col, between=group_col)
    performed_test = 'Mixed-model ANOVA'
    # If we found some non-parametric alternative this could be implemented here
    if parametric == False:
        print ("Please be aware that the data require non-parametric testing.\n\
        However, this is not implemented yet and a parametric test is computed instead.")

    d_results['summary']['pairwise_comparisons'] = pg.pairwise_ttests(data=df, dv=data_col,
                                                                   within=session_col, subject=subject_col,
                                                                   between=group_col, padjust='holm')

    d_results['data_col'] = data_col
    d_results['group_col'] = group_col
    d_results['subject_col'] = subject_col
    d_results['session_col'] = session_col
    d_results['l_groups'] = l_groups
    d_results['l_sessions'] = l_sessions
    d_results['performed_test'] = performed_test

    return d_results