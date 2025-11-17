# import pandas as pd
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

# Import data
df = conf.get_data()
# bouts_df = conf.get_bouts_df()
# bouts_df = bouts_df[bouts_df['state'] == 'included']

# Import statistical results from Lauren Cassidy
data_model, data_points, data_sessions = conf.get_bayes()

# Import and plotting paramaters
plot_param = conf.get_plot()
tasks_order = conf.get_analysis()['tasks_order']
animal_list = data_points.sort_values(by=['group', 'animal'])['animal'].unique()
data_model = data_model.sort_values(by=['selection', 'animal'], ascending=False)

# Set plotting styles
sns.set(style="whitegrid")
sns.set_context("paper")

# ======== FIGURE 4B
Figure_3B_height = (180 / 25.4) * plot_param['sizeMult']
Figure_3B_width = (180 / 25.4) * plot_param['sizeMult']

fig, ax = plt.subplots(4, 4, sharex=False, sharey=True, figsize=(Figure_3B_width, Figure_3B_height))
fig.suptitle('Choice proportions and model estimates (95% CI)', fontsize=plot_param['titleFontSize'])
ax = ax.flatten()

data_sessions['trial_norm'] = data_sessions['trials'] / max(data_sessions['trials'].values)
data_sessions['estimate'] = data_sessions['estimate'].astype(float)
size_thick = (10, 150)

for i, a in enumerate(animal_list):

    plot_df = data_sessions[data_sessions['animal'] == a]
    plot_df['x_order'] = plot_df['selection'].replace({'static': 0, 'dynamic': 1, 'pictures': 2})
    plot_df = plot_df.sort_values(by='x_order').reset_index(drop=True)

    sns.color_palette('Set1')
    g = sns.scatterplot(data=plot_df, alpha=0.5, ax=ax[i],
                            x='session', y='estimate', hue='selection',
                            size='trial_norm', sizes=(10, 150), legend= i/15 == 1)

    f = sns.regplot(data=plot_df[plot_df['selection'] == 'static'], ax=ax[i], x='session', y='estimate',
                    ci=False, logistic=False, scatter=False)
    f = sns.regplot(data=plot_df[plot_df['selection'] == 'dynamic'], ax=ax[i], x='session', y='estimate',
                    ci=False, logistic=False, scatter=False)
    f = sns.regplot(data=plot_df[plot_df['selection'] == 'pictures'], ax=ax[i], x='session', y='estimate',
                    ci=False, logistic=False, scatter=False)

    ax[i].set_xlabel(xlabel=None)

    if i/15 == 1:
        h, l = ax[i].get_legend_handles_labels()
        handles = [h[2], h[1], h[3], h[4], h[5], h[9]]
        labels = [l[2], l[1], l[3], 'Trials', '< 100', '> 1000']
        ax[i].get_legend().remove()

    # ax[i].set_ylabel(ylabel=None)
    ax[i].set_title(a)
    # ax[i].set_xlim([-0.5, 2.5])
    ax[i].set_xticks(range(1, 7))
    g.set(xticklabels=[], xlabel=None)
    g.set(xticklabels=[], xlabel=None, ylabel=None,
          yticks=[0, 0.33, 0.66, 1], yticklabels=['0', '.33', '.66', '1'])

ax[12].set_ylabel(ylabel='Proportion', fontsize=plot_param['labelFontSize'])
ax[12].set_xticks(range(1,7))
ax[12].set_xticklabels(['1', '2', '3', '4', '5', '6'], fontsize=plot_param['labelFontSize'])
ax[12].set_xlabel('Sessions', fontsize=plot_param['labelFontSize'])
fig.tight_layout()

ax[15].legend(handles, labels, fontsize=plot_param['legendFontSize'],borderpad=0.2,
             loc='lower right', bbox_to_anchor=(1.05, -0.52), ncol=2, fancybox=True, shadow=False)


STAT = pd.DataFrame()
summary_df = data_sessions.groupby(['animal','session', 'selection'])['estimate'].median().reset_index()
for a in summary_df['animal'].unique():
    for s in summary_df['selection'].unique():
        t = pg.partial_corr(x='session', y='estimate',
                            data=summary_df[(summary_df['animal'] == a) & (summary_df['selection'] == s)])
        t['animal'] = a
        t['selection'] = s
        STAT = pd.concat([STAT, t], ignore_index=True)

# Adjust statistics for multiple comparisons
adjusted_p = multipletests(pvals=STAT['p-val'], alpha=0.05, method="b")
STAT['adj_p'] = adjusted_p[1]
STAT['adj_sig'] = adjusted_p[0]

plot_name = 'Figure_S1'
if plot_param['saveplot']:
    NAME = "{}{}{}".format(plot_path, plot_name, '.pdf')
    plt.savefig(NAME, format='pdf')

# ==============================================================
# SAVE TABLE + DESCRIPTION FOR FIGURE S1
# ==============================================================
if plot_param['savetable']:
    # ---- CSV ----
    NAME = f"{results_path}{plot_name}.csv"
    STAT = STAT.reindex(columns=["animal", "selection", "r", "CI95%", "p-val", "adj_p", "adj_sig"])
    STAT['r'] = np.round(STAT['r'], 2)
    STAT['p-val'] = np.round(STAT['p-val'], 4)
    STAT['adj_p'] = np.round(STAT['adj_p'], 4)
    STAT.to_csv(NAME, sep=';', decimal='.', index=False)

    # ---- DESCRIPTION ----
    desc_path = f"{results_path}Figure_S1_description.txt"
    with open(desc_path, "w") as f:
        f.write("""
====================================================================
FIGURE S1 — Session-wise correlations of model estimates
====================================================================
File: Figure_S1.csv

Each row represents one animal and one task condition, and reports the
correlation between session number and the modeled estimate of choice
proportion.

Columns:
- animal: Animal identifier.
- selection: Task condition ('static', 'dynamic', or 'pictures').
- r: Partial correlation coefficient between session index and the
     model estimate of choice proportion for that condition.
- CI95%: 95 % confidence interval for the correlation coefficient.
- p-val: Unadjusted p-value of the correlation.
- adj_p: P-value after Benjamini–Hochberg correction for multiple
         comparisons.
- adj_sig: Boolean flag indicating whether the adjusted p-value is
           below the chosen significance threshold.

--------------------------------------------------------------------
Numeric values are rounded to two or four decimal places as appropriate.
""")