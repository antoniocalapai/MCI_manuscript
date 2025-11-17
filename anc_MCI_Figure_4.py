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
tasks_order = conf.get_analysis()['tasks_order']
minSize = conf.get_analysis()['bout_minSize']

# Set plotting styles
sns.set(style="whitegrid")
sns.set_context("paper")

# ==============================================================
# Load the curated dataframes
static_df, dynamic_df, psycho_df = conf.get_performance()

# ==============================================================
figure4AB_height = (60 / 25.4) * plot_param['sizeMult']
figure4AB_width = (180 / 25.4) * plot_param['sizeMult']

f, ax = plt.subplots(1, 3, figsize=(figure4AB_width, figure4AB_height), sharey=False, constrained_layout=True)

g = sns.pointplot(x='size', y='HR',
                  estimator=np.median, errorbar=("pi", 50),
                  data=static_df, color="black", ax=ax[0])

g = sns.pointplot(x='size', y='chance', markers='', linestyles='--',
                  data=static_df, color="grey", ax=ax[0])

ax[0].set_xlabel(xlabel='Stimulus size', fontsize=plot_param['labelFontSize'])
ax[0].set_ylabel(ylabel='Hit rate', fontsize=plot_param['labelFontSize'])
ax[0].tick_params(labelsize=8)
ax[0].set_ylim(0, 1)
ax[0].set_title('Static Task', fontsize=plot_param['labelFontSize'])

# Dynamic Task
g = sns.lineplot(x='speed', y='wHR', size='size', sizes=(1, 5),
                 legend=True, ci=None,
                 data=dynamic_df, color="black", alpha=.25, ax=ax[1])

ax[1].set_xlabel(xlabel='Speed', fontsize=plot_param['labelFontSize'])
ax[1].set_ylabel(ylabel='Adjusted hit rate', fontsize=plot_param['labelFontSize'])
ax[1].tick_params(labelsize=8)
ax[1].set_ylim(0, 1)
ax[1].set_xlim(10, 30)
ax[1].set_title('Dynamic Task', fontsize=plot_param['labelFontSize'])

handles, labels = ax[1].get_legend_handles_labels()
handles = [handles[0], handles[-1]]
labels = [labels[0], labels[-1]]
g.legend(handles, labels, loc='lower center', ncol=2,
         columnspacing=0.5, frameon=False, title="size", fontsize=8)

# Hit Rate across sessions
g = sns.lineplot(data=dynamic_df, ci=None, legend=True, color="black",
                 x="session_relative", y="wHR", hue='speed', ax=ax[2])

ax[2].set_ylim(0, 1)
handles, labels = ax[2].get_legend_handles_labels()
handles = [handles[0], handles[-1]]
labels = [10, 30]
g.legend(handles, labels, loc='lower center', ncol=2,
         columnspacing=0.5, frameon=True, title="speed", fontsize=8)

ax[2].set_xticks([1, 2, 3, 4, 5, 6])
ax[2].set_xlim(1, 6)
ax[2].tick_params(labelsize=8)
ax[2].set_xlabel(xlabel='Session', fontsize=plot_param['labelFontSize'])
ax[2].set_ylabel(ylabel=None)
ax[2].set_yticklabels([])

plot_name = 'Figure_4AB'
if plot_param['saveplot']:
    NAME = "{}{}{}".format(plot_path, plot_name, '.pdf')
    plt.savefig(NAME, format='pdf')

# ==============================================================
# Figure 4B: adjusted hit rate vs size and speed
figure4C_height = (45 / 25.4) * plot_param['sizeMult']
figure4C_width = (120 / 25.4) * plot_param['sizeMult']

wHR_df = dynamic_df.groupby(['size', 'speed'])['wHR'].mean().reset_index()
wHR_df['speed'] = wHR_df['speed'].astype(int)

# Create a pivot table with switched axes
pivot_table = pd.pivot_table(wHR_df, values='wHR', index='size', columns='speed')

# Create a figure with the desired width and aspect ratio
fig, ax = plt.subplots(figsize=(figure4C_width, figure4C_height))

# Create a 2D heatmap using seaborn
g = sns.heatmap(pivot_table, cmap='magma', ax=ax,
                cbar_kws={'aspect': 10, "pad": 0.01, 'label': 'Adjusted Hit Rate'})
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
ax.invert_yaxis()

ax.tick_params(labelsize=plot_param['tickFontSize'])
ax.set_xlabel(xlabel='Speed', fontsize=plot_param['labelFontSize'])
ax.set_ylabel(ylabel='Size', fontsize=plot_param['labelFontSize'])
ax.set_title('Average adjusted hit rate across all animals', fontsize=plot_param['labelFontSize'])

fig.tight_layout()

plot_name = 'Figure_4C'
if plot_param['saveplot']:
    NAME = "{}{}{}".format(plot_path, plot_name, '.pdf')
    plt.savefig(NAME, format='pdf')

# ==============================================================
# Figure 4D: Scatter of size vs speed sweet spot distributions
figure4D_height = (45 / 25.4) * plot_param['sizeMult']
figure4D_width = (60 / 25.4) * plot_param['sizeMult']

fig, ax = plt.subplots(figsize=(figure4D_width, figure4D_height), constrained_layout=True)
counts = psycho_df.groupby(['speed', 'size']).size().reset_index(name='Count')
counts['speed'] = counts['speed'].astype(int)
g = sns.scatterplot(data=counts, x='speed', y='size', size='Count', sizes=(50, 350), ax=ax)

ax.set_yticks([5, 7, 9])
ax.set_xticks([10, 12, 14, 16, 18, 20])
ax.set_xlim(9, 20)
ax.set_ylim(4.1, 10)
ax.tick_params(labelsize=plot_param['tickFontSize'])
ax.set_xlabel(xlabel='Speed', fontsize=plot_param['labelFontSize'])
ax.set_ylabel(ylabel='Size', fontsize=plot_param['labelFontSize'])
# ax.set_title('Best adjusted hit rate', fontsize=plot_param['labelFontSize'])

handles, labels = ax.get_legend_handles_labels()
handles = [handles[0], handles[-1]]
labels = [1, 7]
g.legend(handles, labels, loc='upper right', ncol=1, borderpad=1.1,
        labelspacing=1, frameon=True, title="Animals", fontsize=8)

plot_name = 'Figure_4D'
if plot_param['saveplot']:
    NAME = "{}{}{}".format(plot_path, plot_name, '.pdf')
    plt.savefig(NAME, format='pdf')

# ==============================================================
# Statistics on dynamic task by animal
STAT = pd.DataFrame()
summary_df = dynamic_df.groupby(['group','animal','speed'])['wHR'].median().reset_index()
total_df = dynamic_df.groupby('animal')['total'].sum().reset_index()
for a in summary_df['animal'].unique():
    t = pg.partial_corr(x='speed', y='wHR', data=summary_df[summary_df['animal'] == a])
    t['animal'] = a
    t['trials'] = total_df[total_df['animal']==a]['total'].values[0]
    t['group'] = dynamic_df[dynamic_df['animal']==a]['group'].values[0]

    STAT = pd.concat([STAT, t], ignore_index=True)

# Adjust statistics for multiple comparisons
adjusted_p = multipletests(pvals=STAT['p-val'], alpha=0.05, method="b")
STAT['adj_p'] = adjusted_p[1]
STAT['adj_sig'] = adjusted_p[0]

# ==============================================================
# SAVE TABLES FOR EACH PANEL IN FIGURE 4
# ==============================================================

if plot_param['savetable']:
    # --------------------------
    # FIGURE 4A — Static task performance by stimulus size
    # --------------------------
    table_4A = static_df.groupby('size')[['HR', 'chance']].median().reset_index()
    table_4A['HR'] = np.round(table_4A['HR'], 3)
    table_4A['chance'] = np.round(table_4A['chance'], 3)
    NAME = f"{results_path}Figure_4A.csv"
    table_4A.to_csv(NAME, sep=';', decimal='.', index=False)

    # --------------------------
    # FIGURE 4B — Dynamic task: adjusted hit rate vs. speed and size
    # (animal-level statistics already computed in STAT)
    # --------------------------
    NAME = f"{results_path}Figure_4B.csv"
    STAT = STAT.reindex(columns=["group", "animal", "r", "CI95%", "n", "trials", "p-val", "adj_p", "adj_sig"])
    STAT['r'] = np.round(STAT['r'], 2)
    STAT['adj_p'] = np.round(STAT['adj_p'], 4)
    STAT['p-val'] = np.round(STAT['p-val'], 4)
    STAT.to_csv(NAME, sep=';', decimal='.', index=False)

    # --------------------------
    # FIGURE 4C — Mean adjusted hit rate heatmap (size × speed)
    # --------------------------
    table_4C = wHR_df.copy()
    table_4C = table_4C.reindex(columns=['size', 'speed', 'wHR'])
    table_4C['wHR'] = np.round(table_4C['wHR'], 3)
    NAME = f"{results_path}Figure_4C.csv"
    table_4C.to_csv(NAME, sep=';', decimal='.', index=False)

    # --------------------------
    # FIGURE 4D — Frequency of optimal size/speed combinations (“sweet spots”)
    # --------------------------
    table_4D = counts.copy()
    table_4D = table_4D.reindex(columns=['speed', 'size', 'Count'])
    NAME = f"{results_path}Figure_4D.csv"
    table_4D.to_csv(NAME, sep=';', decimal='.', index=False)

if plot_param['savetable']:
    desc_path = f"{results_path}Figure_4_description.txt"
    with open(desc_path, "w") as f:
        f.write("""
====================================================================
FIGURE 4A — Static task performance by stimulus size
--------------------------------------------------------------------
File: Figure_4A.csv

Each row summarises the median hit rate and chance level across all animals
for a given stimulus size in the static task.

Columns:
- size: Stimulus diameter (visual angle units).
- HR: Median hit rate across all animals for that stimulus size.
- chance: Theoretical chance-level performance as a function of stimulus size/background.

--------------------------------------------------------------------
FIGURE 4B — Dynamic task: speed-performance modulation per animal
--------------------------------------------------------------------
File: Figure_4B.csv

Each row corresponds to one animal’s partial correlation between stimulus speed and
adjusted hit rate (wHR) in the dynamic task.

Columns:
- group: Experimental group identifier.
- animal: Animal identifier.
- r: Partial correlation coefficient between speed and wHR.
- CI95%: 95% confidence interval of the correlation coefficient.
- n: Number of speed–wHR samples used.
- trials: Total dynamic‐task trials for that animal.
- p-val: Unadjusted p‐value of the correlation.
- adj_p: P-value adjusted for multiple comparisons (Benjamini–Hochberg).
- adj_sig: Boolean indicating whether adj_p is below threshold.

--------------------------------------------------------------------
FIGURE 4C — Mean adjusted hit rate for size × speed combinations
--------------------------------------------------------------------
File: Figure_4C.csv

Each row reports the mean adjusted hit rate (wHR) for a specific stimulus size and speed,
averaged across all animals.

Columns:
- size: Stimulus diameter (visual angle units).
- speed: Target‐movement speed (visual angle units per second).
- wHR: Mean adjusted hit rate across animals for that size–speed pair.

--------------------------------------------------------------------
FIGURE 4D — Frequency of optimal size–speed “sweet-spots”
--------------------------------------------------------------------
File: Figure_4D.csv

Each row indicates how many animals showed a particular size–speed combination
as their highest adjusted hit-rate condition.

Columns:
- speed: Target‐movement speed (visual angle units per second).
- size: Stimulus diameter (visual angle units).
- Count: Number of animals for whom that size–speed combination was optimal.

--------------------------------------------------------------------
Numeric values are rounded to three or four decimal places as appropriate.
""")