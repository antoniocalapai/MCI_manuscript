# -*- coding: utf-8 -*-
"""
This script generates the plots of Figure 2 (with relative summary tables) of the manuscript:
"A touchscreen-based, multiple-choice approach to cognitive enrichment of captive rhesus macaques (Macaca mulatta)"
Antonino Calapai*, Dana Pfefferle, Lauren C. Cassidy, Pinar Yurt, Ralf R. Brockhausen, Stefan True

*script author: acalapai@dpz.eu

June-July 2022

list of output files:

"""
import datetime as dt
from pathlib import Path
from scipy.stats import friedmanchisquare
from statsmodels.stats.multitest import multipletests
import scipy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pingouin as pg
import os

# =============================================
# Setting analysis parameters
binSize = 10
minSize = 10
x_bins = 100
# animal_list = ['al', 'ba', 'ni', 'ea', 'pi', 'de', 'el', 'vi', 'he', 'pa', 'sa']
# =============================================
# Setting plotting parameters
sizeMult = 1
saveplot = 0
savetable = 1

tickFontSize = 8
labelFontSize = 10
titleFontSize = 10
lineWidth = 1
lineAlpha = 0.8

sns.set(style="whitegrid")
sns.set_context("paper")

plot_nameA = 'Figure_S2A'
plot_nameB = 'Figure_S2B'
result_filename = "analysis_python/plots/Figure_S2.csv"
pd.options.mode.chained_assignment = None

# =============================================
# Open the csv file and import the DATA
PLOT_path = 'analysis_python/plots/'
directory_name = Path("dataframes/")

data_files = os.listdir(directory_name)
data_files = sorted(list(filter(lambda f: f.endswith('.csv'), data_files)))

csv_file = directory_name / data_files[-1]

# =============================================
# Load and filter dataset
df = pd.read_csv(csv_file, low_memory=False, decimal=',')

# assign unique number identifier to groups
df.loc[df.group == 'alwcla', 'group'] = 1
df.loc[df.group == 'bacnil', 'group'] = 2
df.loc[df.group == 'casear', 'group'] = 3
df.loc[df.group == 'curpin', 'group'] = 4
df.loc[df.group == 'derelm', 'group'] = 5
df.loc[df.group == 'natvin', 'group'] = 6
df.loc[df.group == 'heilotpansan', 'group'] = 7

df['manual_label'] = df['manual_label'].str[:2]
df.rename(columns={"manual_label": "animal"}, inplace=True)
animal_List = df['animal'].unique()
df = df.reset_index(drop=True)

for group in df.group.unique():
    counter = 0
    for date in df[df.group == group].date.unique():
        counter += 1
        df.loc[(df.group == group) & (df.date == date), 'session_relative'] = counter

# Figure_S2A ================================
tasks_order = list(['static', 'dynamic', 'pictures'])

# Compute task preference across bouts (excluding first bout after set change)
c = ['animal', 'session', 'bout', 'bin', 'proportion', 'selection', 'position', 'group', 'N']
Figure_S2 = pd.DataFrame(columns=c)
plot_DF = df.copy(deep=True)

idx = 0
for a in plot_DF['animal'].unique():
    print("{}{}".format('Processing animal: ', a))
    b_idx = 0
    for s in plot_DF[plot_DF['animal'] == a]['session_relative'].unique():
        for b in plot_DF[(plot_DF['animal'] == a) & (plot_DF['session_relative'] == s)]['bout_ID'].unique():

            T = plot_DF[(plot_DF['animal'] == a) & (plot_DF['session_relative'] == s) & (plot_DF['bout_ID'] == b)]
            T = T.reset_index()

            if (1 in T['setChange_flag'].unique()) & (len(T) >= minSize):

                b_idx = b_idx + 1
                for i in range(0, len(T), binSize):
                    idx = idx + 1

                    for t in tasks_order:
                        df1 = pd.DataFrame(columns=c)

                        df1.loc[idx, 'proportion'] = np.sum(T.loc[i:i + (binSize - 1), 'selection'] == t) / binSize
                        df1.loc[idx, 'selection'] = t
                        df1.loc[idx, 'animal'] = a
                        df1.loc[idx, 'session'] = s
                        df1.loc[idx, 'bin'] = i
                        df1.loc[idx, 'bout'] = b_idx
                        df1.loc[idx, 'group'] = T.group.unique()[0]
                        df1.loc[idx, 'position'] = T.loc[i:i + (binSize - 1), 'selection'].to_numpy()
                        df1.loc[idx, 'N'] = len(T)

                        Figure_S2 = pd.concat([Figure_S2, df1])

Figure_S2 = Figure_S2.sort_values(by=['group', 'animal'], ignore_index=True)
Figure_S2 = Figure_S2[Figure_S2['bin'] <= x_bins]

bouts = Figure_S2.drop_duplicates(['group', 'animal', 'bout'])
bouts = bouts.groupby(['group', 'animal'])['bout'].count().reset_index()
bouts = bouts[bouts['bout'] >= 5]

g = sns.relplot(data=Figure_S2[Figure_S2['animal'].isin(bouts['animal'])], x="bin", y="proportion", hue="selection",
                kind='line', col='animal', col_wrap=int(np.ceil(len(bouts) / 2)), height=1.2, aspect=0.74,
                facet_kws={'sharey': False, 'sharex': False})

g.set(xticklabels=[], xlabel=None, yticklabels=[], ylabel=None, yticks=[0, 0.33, 0.66, 1])
g.set_titles(template='{col_name}')

axes = g.axes.flatten()

for i, m in enumerate(bouts.animal.unique()):
    axes[i].set_title('{}{}{}{}'.format(m, ' (', bouts.bout.to_list()[i], ')'))
    axes[i].set_xticks([0, 50, 100])
    axes[i].set_yticks([0, 0.33, 0.66, 1])

    if i == int(np.ceil(len(bouts) / 2)):

        axes[i].set_xticklabels([0, 50, 100])
        axes[i].set_xlabel(xlabel='Trial')
        axes[i].set_yticklabels([0, 0.33, 0.66, 1])
        axes[i].set_ylabel(ylabel='Proportion')
        # if STAT[STAT['animal'] == m].adj_sig.values[0]:
        #     axes[i].text(2.5, 0.6, '*', color='black', fontsize=20, va="bottom", ha="right")

g.tight_layout()

if saveplot:
    NAME = "{}{}{}".format(PLOT_path, plot_nameA, '.pdf')
    plt.savefig(NAME, format='pdf')

# Figure_S2B ================================
tasks_order = list([-8, 0, 8])

# Compute task preference across bouts (excluding first bout after set change)
c = ['animal', 'session', 'bout', 'bin', 'proportion', 'selection_xpos', 'position', 'group', 'N']
Figure_S2 = pd.DataFrame(columns=c)
plot_DF = df.copy(deep=True)

idx = 0
for a in plot_DF['animal'].unique():
    print("{}{}".format('Processing animal: ', a))
    b_idx = 0
    for s in plot_DF[plot_DF['animal'] == a]['session_relative'].unique():
        for b in plot_DF[(plot_DF['animal'] == a) & (plot_DF['session_relative'] == s)]['bout_ID'].unique():

            T = plot_DF[(plot_DF['animal'] == a) & (plot_DF['session_relative'] == s) & (plot_DF['bout_ID'] == b)]
            T = T.reset_index()

            if (1 in T['setChange_flag'].unique()) & (len(T) >= minSize):

                b_idx = b_idx + 1
                for i in range(0, len(T), binSize):
                    idx = idx + 1

                    for t in tasks_order:
                        df1 = pd.DataFrame(columns=c)

                        df1.loc[idx, 'proportion'] = np.sum(T.loc[i:i + (binSize - 1), 'selection_xpos'] == t) / binSize
                        df1.loc[idx, 'selection_xpos'] = t
                        df1.loc[idx, 'animal'] = a
                        df1.loc[idx, 'session'] = s
                        df1.loc[idx, 'bin'] = i
                        df1.loc[idx, 'bout'] = b_idx
                        df1.loc[idx, 'group'] = T.group.unique()[0]
                        df1.loc[idx, 'position'] = T.loc[i:i + (binSize - 1), 'selection_xpos'].to_numpy()
                        df1.loc[idx, 'N'] = len(T)

                        Figure_S2 = pd.concat([Figure_S2, df1])

Figure_S2 = Figure_S2.sort_values(by=['group', 'animal'], ignore_index=True)
Figure_S2 = Figure_S2[Figure_S2['bin'] <= x_bins]

bouts = Figure_S2.drop_duplicates(['group', 'animal', 'bout'])
bouts = bouts.groupby(['group', 'animal'])['bout'].count().reset_index()
bouts = bouts[bouts['bout'] >= 5]

g = sns.relplot(data=Figure_S2[Figure_S2['animal'].isin(bouts['animal'])], x="bin", y="proportion", hue="selection_xpos",
                kind='line', col='animal', col_wrap=int(np.ceil(len(bouts) / 2)), height=1.2, aspect=0.74,
                facet_kws={'sharey': False, 'sharex': False})

g.set(xticklabels=[], xlabel=None, yticklabels=[], ylabel=None, yticks=[0, 0.33, 0.66, 1])
g.set_titles(template='{col_name}')

axes = g.axes.flatten()

for i, m in enumerate(bouts.animal.unique()):
    axes[i].set_title('{}{}{}{}'.format(m, ' (', bouts.bout.to_list()[i], ')'))
    axes[i].set_xticks([0, 50, 100])
    axes[i].set_yticks([0, 0.33, 0.66, 1])

    if i == int(np.ceil(len(bouts) / 2)):

        axes[i].set_xticklabels([0, 50, 100])
        axes[i].set_xlabel(xlabel='Trial')
        axes[i].set_yticklabels([0, 0.33, 0.66, 1])
        axes[i].set_ylabel(ylabel='Proportion')
        # if STAT[STAT['animal'] == m].adj_sig.values[0]:
        #     axes[i].text(2.5, 0.6, '*', color='black', fontsize=20, va="bottom", ha="right")

g.tight_layout()

if saveplot:
    NAME = "{}{}{}".format(PLOT_path, plot_nameB, '.pdf')
    plt.savefig(NAME, format='pdf')


# ==============================================================
# SAVE TABLES FOR FIGURE S2
# ==============================================================

if savetable:
    # ---------- FIGURE S2A ----------
    # Save task-choice proportions per animal/session/bout/bin
    table_S2A = Figure_S2.copy()
    table_S2A = table_S2A.reindex(columns=[
        'group', 'animal', 'session', 'bout', 'bin',
        'selection', 'proportion', 'N'
    ])
    table_S2A['proportion'] = np.round(table_S2A['proportion'], 3)
    NAME = f"{PLOT_path}{plot_nameA}.csv"
    table_S2A.to_csv(NAME, sep=';', decimal='.', index=False)

    # ---------- FIGURE S2B ----------
    # Save position-choice proportions per animal/session/bout/bin
    table_S2B = Figure_S2.copy()
    table_S2B = table_S2B.reindex(columns=[
        'group', 'animal', 'session', 'bout', 'bin',
        'selection_xpos', 'proportion', 'N'
    ])
    table_S2B['proportion'] = np.round(table_S2B['proportion'], 3)
    NAME = f"{PLOT_path}{plot_nameB}.csv"
    table_S2B.to_csv(NAME, sep=';', decimal='.', index=False)


# =============================================
# DESCRIPTION FILE (Supplementary Figure S2)
# =============================================
if savetable:
    desc_path = f"{PLOT_path}Figure_S2_description.txt"
    with open(desc_path, "w") as f:
        f.write("""
====================================================================
FIGURE S2 — Choice proportions across bouts and trials
====================================================================

This document summarises the content of the CSV tables generated for
Supplementary Figure S2 of Calapai et al., Animals 2023 13(17):2702.

--------------------------------------------------------------------
FIGURE S2A — Choice proportions by task condition
--------------------------------------------------------------------
File: Figure_S2A.csv

Each row contains the proportion of trials assigned to one of the three
task conditions within a given trial bin and bout for each animal.

Columns:
- group: Group identifier.
- animal: Animal identifier.
- session: Session index (relative to start of the experiment).
- bout: Bout number within the session (excluding the first after set change).
- bin: Sequential 10-trial bin index within the bout.
- selection: Task condition ('static', 'dynamic', 'pictures').
- proportion: Fraction of trials (0–1) in that bin corresponding to the condition.
- N: Total number of trials included in that bout.

--------------------------------------------------------------------
FIGURE S2B — Choice proportions by screen position
--------------------------------------------------------------------
File: Figure_S2B.csv

Each row contains the proportion of touches made to each screen position
within a given trial bin and bout for each animal.

Columns:
- group: Group identifier.
- animal: Animal identifier.
- session: Session index (relative to start of the experiment).
- bout: Bout number within the session (excluding the first after set change).
- bin: Sequential 10-trial bin index within the bout.
- selection_xpos: Screen-position code (−8 = left, 0 = centre, 8 = right).
- proportion: Fraction of trials (0–1) in that bin corresponding to the position.
- N: Total number of trials included in that bout.

--------------------------------------------------------------------
All numeric values are rounded to three decimal places.
""")