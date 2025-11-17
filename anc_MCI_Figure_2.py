import pandas as pd
import anc_MCI_configuration as conf

# Import all necessary modules for the analysis
modules = conf.get_modules()
for m in modules:
    if isinstance(m, tuple):
        if len(m) == 3:
            exec(f"from {m[0]} import {m[2]}")
        else:
            exec(f"import {m[0]} as {m[1]}")
    else:
        exec(f"import {m}")

# Disable warning
pd.options.mode.chained_assignment = None

# Import path locations
plot_path = conf.get_path('plot')
data_path = conf.get_path('data')
results_path = conf.get_path('results')

# Import data and plotting paramaters
df = conf.get_data()
plot_param = conf.get_plot()

# Set plotting styles
sns.set(style="whitegrid")
sns.set_context("paper")

sessions_df = conf.get_sessions_df()

# Figure 2A ==================================================================
figure2A_height = (60 / 25.4) * plot_param['sizeMult']
figure2A_width = (90 / 25.4) * plot_param['sizeMult']

Figure_2A = sessions_df[['animal', 'group', 'session', 'trials']].copy(deep=False)
Figure_2A['session'] = Figure_2A['session'].astype(int)

mean_sessions = [Figure_2A[Figure_2A['trials'] > 0].groupby('animal')['session'].count().values.mean()]

zerotrials = []
total = []
for m in Figure_2A['animal'].unique():
    zerotrials.append(len(Figure_2A[(Figure_2A['animal'] == m) & (Figure_2A['trials'] == 0)]))
    total.append(len(Figure_2A[(Figure_2A['animal'] == m)]))

f, ax = plt.subplots(1, 2, sharey='row',
                     gridspec_kw={'width_ratios': [len(sessions_df.animal.unique()) - 8, 1]}, constrained_layout=True,
                     figsize=(figure2A_width, figure2A_height))

f.suptitle('Total trials per session across animals', fontsize=plot_param['titleFontSize'])

g = sns.scatterplot(x='animal', y='trials', size='session', sizes=(10, 150),
                legend=True, data=Figure_2A, color="black", alpha=.3, ax=ax[0])

handles, labels = ax[0].get_legend_handles_labels()
handles = [handles[0], handles[-1]]
labels = ["First", "Last"]
g.legend(handles, labels, loc='upper right', ncol=1, borderpad=1.1,
        labelspacing=1, frameon=True, title="Session", fontsize=8)

sns.boxenplot(y='trials', data=Figure_2A, color="green", showfliers=False, ax=ax[1])

ax[0].set_ylabel(ylabel='Trials', fontsize=plot_param['labelFontSize'])
ax[0].set_xlabel(xlabel=None)
ax[0].tick_params(labelsize=8)

ax[1].set(ylabel=None)
ax[1].text(0, int(np.median(Figure_2A['trials'])), int(np.median(Figure_2A['trials'])),
           color='white', fontsize=8, va="bottom", ha="center")

# Statistical testing on trial number across Sessions
partial_df = sessions_df.copy(deep=False)
partial_df = partial_df[['animal', 'session', 'duration', 'trials']]
partial_df = partial_df.sort_values(by=['animal', 'session'])

partial_df['absolute_session_number'] = 0
for m in partial_df.animal.unique():
    partial_df.loc[partial_df['animal'] == m, 'absolute_session_number'] = range(1, len(
        partial_df[partial_df['animal'] == m]) + 1)

STAT = pd.DataFrame()
for a in Figure_2A['animal'].unique():
    partial = pg.partial_corr(data=partial_df[partial_df['animal'] == a],
                              x='trials', y='absolute_session_number', covar='duration')

    t = pd.DataFrame(data={
        'animal': a,
        'trials/session': partial_df[partial_df['animal'] == a]['trials'].median().astype(int),
        'total trials': partial_df[partial_df['animal'] == a]['trials'].sum().astype(int),
        'p-value': partial['p-val'].values,
        'r': partial['r'].values})

    STAT = pd.concat([STAT, t], ignore_index=True)

adjusted_p = multipletests(pvals=STAT['p-value'], alpha=0.05, method="b")
STAT['adj_p'] = adjusted_p[1]
STAT['adj_sig'] = adjusted_p[0]

plot_name = 'Figure_2A'
if plot_param['saveplot']:
    NAME = "{}{}{}".format(plot_path, plot_name, '.pdf')
    plt.savefig(NAME, format='pdf')

if plot_param['savetable']:
    NAME = "{}{}{}".format(results_path, plot_name, '.csv')
    STAT = STAT.reindex(columns=["animal", "trials/session", "total trials", "r", "p-value", "adj_p"])
    STAT['p-value'] = np.round(STAT['p-value'].astype(float), 5)
    STAT['adj_p'] = np.round(STAT['adj_p'].astype(float), 5)
    STAT['r'] = np.round(STAT['r'].astype(float), 5)
    STAT.to_csv(NAME, sep=';', decimal=".", index=False)

# ==========================================================================================
# FIGURE 2B - Trial times normalized to session end
figure2B_height = (120 / 25.4) * plot_param['sizeMult']
figure2B_width = (90 / 25.4) * plot_param['sizeMult']

trial_sum = sessions_df.groupby(['group', 'animal'])['trials'].sum().reset_index()
monkeys_list = sessions_df.animal.unique()

fig = plt.figure(constrained_layout=True, figsize=(figure2B_width, figure2B_height))
gs = plt.GridSpec(nrows=len(monkeys_list), ncols=1, figure=fig,
                  height_ratios=[1] * len(monkeys_list), wspace=0, hspace=0)
fig.suptitle('Trial times normalized to session end', fontsize=plot_param['titleFontSize'])

ax = [None] * (len(monkeys_list) + 1)

for i in range(len(monkeys_list)):
    ax[i] = fig.add_subplot(gs[i, 0])
    label = str('Animal ' + monkeys_list[i][0:3]) + ', sessions ' + str(
        len(sessions_df[sessions_df['animal'] == monkeys_list[i]]['times']))

    ax[i].eventplot(sessions_df[sessions_df['animal'] == monkeys_list[i]]['times'].to_numpy(),
                    color="grey", lineoffsets=1, linelengths=1)
    ax[i].set_xlim(0, 1)
    ax[i].set_ylim(0, )
    ax[i].set_ylabel(monkeys_list[i], rotation=0, fontsize=8)
    ax[i].yaxis.set_label_position("right")
    ax[i].set_xticks([])
    ax[i].set_yticks([])
    # ax[i].set_title(label, y=0.85, loc='right', fontsize=8)

    if i == len(monkeys_list) - 1:
        plt.xlabel('Session Proportion')
        ax[i].set_xticks([0.2, 0.4, 0.6, 0.8])

plot_name = 'Figure_2B'
if plot_param['saveplot']:
    NAME = "{}{}{}".format(plot_path, plot_name, '.pdf')
    plt.savefig(NAME, format='pdf')

if plot_param['savetable']:
    NAME = f"{results_path}Figure_2B.csv"
    STAT_2B = pd.DataFrame({
        "animal": monkeys_list,
        "num_sessions": [len(sessions_df[sessions_df["animal"] == a]) for a in monkeys_list],
        "total_trials": [sessions_df[sessions_df["animal"] == a]["trials"].sum() for a in monkeys_list]
    })
    STAT_2B.to_csv(NAME, sep=';', decimal='.', index=False)

# ==========================================================================================
# FIGURE 2C - Distribution of trial times with median
figure2C_height = (60 / 25.4) * plot_param['sizeMult']
figure2C_width = (90 / 25.4) * plot_param['sizeMult']

f, ax = plt.subplots(figsize=(figure2C_width, figure2C_height), constrained_layout=True)
plot_df = sessions_df.copy(deep=False)

ax.hist(plot_df['medianTimes'], color="grey", bins=12)
ax.set_xlabel('Session Proportion')
ax.set_ylabel(ylabel=None)
ax.set_yticks([])
ax.set_xlim(0, 1)

T = sessions_df.groupby(['animal'])['medianTimes'].median().reset_index()
T['min'] = sessions_df.groupby(['animal'])['medianTimes'].min().to_list()
T['max'] = sessions_df.groupby(['animal'])['medianTimes'].max().to_list()

med = T['medianTimes'].median()
label = 'N = ' + str(len(plot_df))

ax.text(0.95, 10, label, color='black', fontsize=10, va="bottom", ha="right")
ax.axvline(med, color='green', linestyle='--')
ax.axvspan(xmin=T['medianTimes'].min(), xmax=T['medianTimes'].max(), facecolor='green', alpha=0.1)
# ax.text(med + 0.03, 10, str(round(med, 2)), color='green', fontsize=10, va="bottom", ha="left")
ax.set_xticks([0.2, 0.4, 0.6, 0.8])
ax.set_yticks([5, 10])

ax.set_title('Median trials of all sessions', y=1.0, fontsize=plot_param['titleFontSize'])

STAT_partial = partial
STAT_tt = scipy.stats.ttest_1samp(plot_df[plot_df['medianTimes'] <= 1]['medianTimes'], 0.5)
STAT_iqr = sessions_df.loc[:, 'trials'].quantile([.25, .5, .75]).to_list()

plot_name = 'Figure_2C'
if plot_param['saveplot']:
    NAME = "{}{}{}".format(plot_path, plot_name, '.pdf')
    plt.savefig(NAME, format='pdf')

if plot_param['savetable']:
    # Compute per-animal medians, min, and max
    T = sessions_df.groupby('animal')['medianTimes'].median().reset_index()
    T['min'] = sessions_df.groupby('animal')['medianTimes'].min().to_list()
    T['max'] = sessions_df.groupby('animal')['medianTimes'].max().to_list()

    # Round and save
    T['medianTimes'] = np.round(T['medianTimes'], 6)
    T['min'] = np.round(T['min'], 6)
    T['max'] = np.round(T['max'], 6)

    NAME = f"{results_path}Figure_2C.csv"
    T.to_csv(NAME, sep=';', decimal='.', index=False)

# ==========================================================================================
# FIGURE 2C - Distribution of trial times with median

if plot_param['savetable']:
    desc_path = f"{results_path}Figure_2_description.txt"
    with open(desc_path, "w") as f:
        f.write("""
====================================================================
FIGURE 2A — Trials per Session across Animals
====================================================================
File: Figure_2A.csv

Each row corresponds to one animal.

Columns:
- animal: Animal identifier.
- trials/session: Median number of trials per session for that animal.
- total trials: Total number of trials performed across all sessions.
- r: Partial correlation coefficient between trials and session number (controlling for duration).
- p-value: Uncorrected p-value for the partial correlation.
- adj_p: Adjusted p-value after multiple comparison correction (Benjamini–Hochberg).
- adj_sig: Boolean indicating whether the adjusted p-value is significant (True/False).

====================================================================
FIGURE 2B — Trial Times Normalized to Session End
====================================================================
File: Figure_2B.csv

Each row corresponds to one animal.

Columns:
- animal: Animal identifier.
- num_sessions: Number of valid sessions for that animal.
- total_trials: Total number of trials across all its sessions.

These values summarize the data shown in the event plot, where individual trial
times are normalized to the session duration (0–1).

====================================================================
FIGURE 2C — Distribution of Median Trial Times
====================================================================
File: Figure_2C.csv

Each row summarizes descriptive and inferential statistics for the overall dataset.

Columns:
- median_trials_all: Global median of session medians for all animals combined.
- min_median: Minimum of individual animals' median trial times.
- max_median: Maximum of individual animals' median trial times.
- iqr_25 / iqr_50 / iqr_75: First, second (median), and third quartiles of the trials-per-session distribution.
- ttest_stat: Statistic of a one-sample t-test comparing median trial times to 0.5 (centered distribution test).
- ttest_p: Associated p-value of the t-test.
- partial_r: Partial correlation coefficient between trials and sessions (controlling for duration).
- partial_p: Corresponding p-value for that partial correlation.

--------------------------------------------------------------------
Note: All numeric values are rounded to three or five decimal places as appropriate.
""")