"""
Configuration file for the data analysis of the MCI project.
- get_modules
    it returns a list of modules necessary for the analysis

- get_data
    it returns the curated dataframe

- get_path_*
    it returns the relevant paths of the project:
    - dataframes
    - plots

- get_plot_*
    it returns the settings for the plot:
    - sizeMultiplicator
    - saveplot
    - savetable
    - tickFontSize
    - labelFontSize
    - titleFontSize
    - sns_style
    - sns_context

- get_session
    it returns a new dataframe based on sessions (rows)

- get_bouts
    it returns a new dataframe based on bouts (rows)

- get_betas
    it returns a new dataframe with beta values from the bayesian analysis

- get_performance
author acalapai@dpz.eu
"""
from pathlib import Path
import os
import pandas as pd
import numpy as np

plot_path = './plots/'
data_path = './dataframes/'
results_path = './results/'

sizeMult = 1
saveplot = 0
savetable = 1

tickFontSize = 8
labelFontSize = 10
legendFontSize = 9
titleFontSize = 10

tasks_order = ['static', 'dynamic', 'pictures']

def get_modules():
    modules = [("statsmodels.stats.multitest", "ONLY", "multipletests"),
               ("pathlib", "ONLY", "Path"),
               ("matplotlib.pyplot", "plt"),
               ("matplotlib", "mpl"),
               ("ipywidgets", "wj"),
               ("pandas", "pd"),
               ("numpy", "np"),
               ("seaborn", "sns"),
               ("pingouin", "pg"),
               ("fit_psyche", "psy"),
               "scipy",
               "os",
               "sys",
               "math"]
    return modules


def get_path(whichpath):
    if 'plot' in whichpath:
        return plot_path
    if 'data' in whichpath:
        return data_path
    if 'results' in whichpath:
        return results_path


def get_data():
    data_files = os.listdir(data_path)
    data_files = sorted(list(filter(lambda f: f.endswith('.csv'), data_files)))
    data_file = data_path + data_files[-1]

    df = pd.read_csv(data_file, low_memory=False, decimal=',')
    df = df[(df['version'] == 'v04') |
            ((df['group'] == 'natvin') & (df['version'] == 'v02') |
             (df['group'] == 'casear') & (df['version'] == 'v02'))]

    # out = df[['group', 'version', 'session_relative']].value_counts().sort_index()
    df['manual_label'] = df['manual_label'].str[:2]
    df.rename(columns={"manual_label": "animal"}, inplace=True)

    groups_map = dict(zip(df.group.unique(), range(1, len(df.group.unique()) + 1)))
    df = df.replace({'group': groups_map}).reset_index(drop=True)
    return df


def get_analysis():
    parameters = dict({'bout_minSize': 10,
                       'tasks_order': tasks_order})
    return parameters


def get_plot():
    parameters = dict({'sizeMult': sizeMult,
                       'saveplot': saveplot,
                       'savetable': savetable,
                       'tickFontSize': tickFontSize,
                       'labelFontSize': labelFontSize,
                       'titleFontSize': titleFontSize,
                       'legendFontSize': legendFontSize,
                       'lineWidth': 1,
                       'lineAlpha': 0.8})
    return parameters


def get_sessions_df():
    df = get_data()
    T = df.groupby(['animal', 'session_relative'])['trial'].count().reset_index()

    sessions_df = pd.DataFrame()
    for group in df.group.unique():
        # print("-" + " Processing data from group " + str(group))
        for session in df[df['group'] == group].session_relative.unique():

            if len(df[(df['group'] == group) & (df['session_relative'] == session)]) > 0:
                unique_animals = df[(df['group'] == group) & (df['session_relative'] == session)]['animal'].unique()

                # cycle through the animals expected in the session
                for monkey in unique_animals:
                    # create a table (A) with the animal information
                    A = df[(df['group'] == group) & (df['session_relative'] == session) & (df['animal'] == monkey)]
                    A = A.reset_index(drop=True)

                    # create a table (B) with the session information
                    B = df[(df['group'] == group) & (df['session_relative'] == session)]
                    B = B.reset_index(drop=True)

                    # look for trials initiated by the animal in table A
                    if len(A) > 0:
                        # extract all trial start times
                        times = list(A['trial_start'] / A['trial_start'].values[-1])
                        abs_times = list(A['trial_start'].values)

                        # calculate the median of all start trial times
                        medianTimes = np.median(times)

                    # if there are no trials from animal A in this session
                    else:
                        # assign nans to missing information
                        times = np.nan
                        medianTimes = np.nan

                    # temp = pd.DataFrame()
                    # temp['group'] = group
                    # temp['session'] = session
                    # temp['duration'] = int(B.session_end[0] / 60000000)
                    # temp['animal'] = monkey
                    # temp['trials'] = len(A)
                    # temp['times'] = list(times)
                    # temp['abs_times'] = list(abs_times)
                    # temp['medianTimes'] = medianTimes

                    temp_df = pd.DataFrame(data={
                        'group': group,
                        'session': session,
                        'duration': int(B.session_end[0] / 60000000),
                        'animal': monkey,
                        'trials': len(A),
                        'times': [times],
                        'abs_times': [abs_times],
                        'medianTimes': medianTimes})

                    sessions_df = pd.concat([sessions_df, temp_df], ignore_index=True)


                    # sessions_df = sessions_df.append({
                    #     'group': group,
                    #     'session': session,
                    #     'duration': int(B.session_end[0] / 60000000),
                    #     'animal': monkey,
                    #     'trials': len(A),
                    #     'times': times,
                    #     'abs_times': abs_times,
                    #     'medianTimes': medianTimes},
                    #     ignore_index=True)

    sessions_df = sessions_df.sort_values(by=['group', 'animal', 'session']).reset_index()
    return sessions_df


def get_bayes():
    data_model = data_path + 'MCI_BayesModel_LC_20230602.csv'
    data_model = pd.read_csv(data_model, low_memory=False, sep=';', decimal=',')
    data_model['animal'] = data_model['animal'].str[:2]

    data_points = data_path + 'MCI_BayesPoints_LC_20230602.csv'
    data_points = pd.read_csv(data_points, low_memory=False, sep=';', decimal=',')
    data_points['animal'] = data_points['animal'].str[:2]
    groups_map = dict(zip(data_points.group.unique(), range(1, len(data_points.group.unique()) + 1)))
    data_points = data_points.replace({'group': groups_map}).reset_index(drop=True)

    data_sessions = data_path + 'MCI_BayesModelSessions_LC_20230612.csv'
    data_sessions = pd.read_csv(data_sessions, low_memory=False, sep=';', decimal=',')
    data_sessions['animal'] = data_sessions['animal'].str[:2]

    return data_model, data_points, data_sessions


def get_performance():
    df = get_data()

    # The chance levels for stimuli of 5, 6, 7, 8, 9, and 10 degrees of visual angles on a screen
    # at a distance of 24 cm are approximately 7.33%, 10.53%, 14.41%, 18.81%, 23.99%, and 30.24% respectively.
    chance_map = dict(zip(sorted(df['size'].unique()), list([7.33, 10.53, 14.41, 18.81, 23.99, 30.24])))

    # First compute performance for the Static Task
    temp = df[['animal', 'session_relative', 'selection', 'size', 'outcome']]
    temp = temp[temp['outcome'] != 'picture']  # Remove faulty outcomes
    temp = temp[temp['selection'] != 'pictures']  # Only consider static task

    static_df = temp.groupby(['animal', 'session_relative', 'size'])['outcome'].count().reset_index()
    static_df['hits'] = 0
    for i in range(0, len(static_df)):
        static_df.loc[i, 'hits'] = len(temp[(temp['animal'] == static_df.loc[i, 'animal']) &
                                            (temp['session_relative'] == static_df.loc[i, 'session_relative']) &
                                            (temp['size'] == static_df.loc[i, 'size']) &
                                            (temp['outcome'] == 'hit')])

    static_df = static_df.rename(columns={'outcome': 'total'})
    static_df['HR'] = static_df['hits'] / static_df['total']
    static_df['chance'] = static_df['size']
    static_df = static_df.replace({'chance': chance_map}).reset_index(drop=True)
    static_df['chance'] /= 100
    static_df['wHR'] = static_df['HR'] - static_df['chance']

    # Then compute performance for the Dynamic Task
    temp = df[['group', 'animal', 'session_relative', 'selection', 'speed', 'size', 'outcome']]
    temp = temp[temp['outcome'] != 'picture']  # Remove faulty outcomes
    temp = temp[temp['selection'] == 'dynamic']  # Only consider static task

    dynamic_df = temp.groupby(['group', 'animal', 'session_relative', 'size', 'speed'])['outcome'].count().reset_index()
    dynamic_df['hits'] = 0

    for i in range(0, len(dynamic_df)):
        dynamic_df.loc[i, 'hits'] = len(temp[(temp['animal'] == dynamic_df.loc[i, 'animal']) &
                                             (temp['session_relative'] == dynamic_df.loc[i, 'session_relative']) &
                                             (temp['speed'] == dynamic_df.loc[i, 'speed']) &
                                             (temp['size'] == dynamic_df.loc[i, 'size']) &
                                             (temp['outcome'] == 'hit')])

    dynamic_df = dynamic_df.rename(columns={'outcome': 'total'})
    dynamic_df['HR'] = dynamic_df['hits'] / dynamic_df['total']
    dynamic_df['chance'] = dynamic_df['size']
    dynamic_df = dynamic_df.replace({'chance': chance_map}).reset_index(drop=True)
    dynamic_df['wHR'] = dynamic_df['HR'] - (dynamic_df['chance'] / 100)

    # Compute sweet spot
    psycho_df = dynamic_df.groupby(['animal', 'size', 'speed'])[['total', 'hits']].sum().reset_index()
    psycho_df['HR'] = psycho_df['hits'] / psycho_df['total']
    chance_map = dict(zip(sorted(df['size'].unique()), list([7.33, 10.53, 14.41, 18.81, 23.99, 30.24])))
    psycho_df['chance'] = psycho_df['size']
    psycho_df = psycho_df.replace({'chance': chance_map}).reset_index(drop=True)
    psycho_df['chance'] /= 100
    psycho_df['wHR'] = psycho_df['HR'] - psycho_df['chance']

    psycho_df = psycho_df.loc[psycho_df.groupby('animal')['wHR'].idxmax(), ['animal', 'speed', 'size']]
    # sns.lineplot(data=psycho_df, x='speed', y='wHR')
    # sns.histplot(data=result, x='speed')

    return static_df, dynamic_df, psycho_df

#
# def get_RT():
#     # Compute performance adjusted by the chance level and the reaction time
#     df = get_data()
#     df = df[(df['selection'] == 'dynamic')
#             & (df['outcome'] == 'hit')].reset_index(drop=True)
#     df['RT'] = df['outcomeTime'] - df['trial_start']
#
#     RT_df = pd.DataFrame()
#     for s in df['speed'].unique():
#         for z in df[(df['speed'] == s)]['size'].unique():
#             T = df[(df['speed'] == s) & (df['size'] == z)]
#
#             RT_df = RT_df.append({
#                 'HR': sum(T['outcome'] == 'hit') / len(T),
#                 'meanRT': np.mean(T[T['outcome'] == 'hit']['RT']),
#                 'speed': s,
#                 'size': z,
#             }, ignore_index=True)
#
#     chance_map = dict(zip(sorted(RT_df['size'].unique()), list([7.33, 10.53, 14.41, 18.81, 23.99, 30.24])))
#     RT_df['chance'] = RT_df['size']
#     RT_df = RT_df.replace({'chance': chance_map}).reset_index(drop=True)
#     RT_df['wHR'] = RT_df['HR'] - (RT_df['chance'] / 100)
#
#     return RT_df