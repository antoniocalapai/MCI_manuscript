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

# =============================================
# FIGURE 3A
Figure_3A_height = (180 / 25.4) * plot_param['sizeMult']
Figure_3A_width = (180 / 25.4) * plot_param['sizeMult']

fig, ax = plt.subplots(4, 4, sharex=False, sharey=True, figsize=(Figure_3A_width, Figure_3A_height))
fig.suptitle('Choice proportions and model estimates (95% CI)', fontsize=plot_param['titleFontSize'])
ax = ax.flatten()

data_points['trial_norm'] = data_points['trial'] / max(data_points['trial'].values)
size_thick = (10, 150)

for i, a in enumerate(animal_list):

    plot_df = data_points[data_points['animal'] == a]
    plot_df['x_order'] = plot_df['selection'].replace({'static': 0, 'dynamic': 1, 'pictures': 2})
    plot_df = plot_df.sort_values(by='x_order').reset_index(drop=True)

    g = sns.scatterplot(data=plot_df, alpha=0.5, palette='cubehelix', ax=ax[i],
                            x='selection', y='estimate', hue='selection_position',
                            size='trial_norm', sizes=(10, 150), legend= i/15 == 1)

    g = sns.stripplot(x="selection", y="estimate", order=tasks_order, color='black',
                      jitter=False, data=data_model[data_model['animal'] == a], ax=ax[i])

    lCI = [data_model[(data_model['animal'] == a) & (data_model['selection'] == 'static')]['lower_CI'].values[0],
           data_model[(data_model['animal'] == a) & (data_model['selection'] == 'dynamic')]['lower_CI'].values[0],
           data_model[(data_model['animal'] == a) & (data_model['selection'] == 'pictures')]['lower_CI'].values[0]]
    uCI = [data_model[(data_model['animal'] == a) & (data_model['selection'] == 'static')]['upper_CI'].values[0],
           data_model[(data_model['animal'] == a) & (data_model['selection'] == 'dynamic')]['upper_CI'].values[0],
           data_model[(data_model['animal'] == a) & (data_model['selection'] == 'pictures')]['upper_CI'].values[0]]

    ax[i].vlines(x=[0, 1, 2], ymin=lCI, ymax=uCI, colors='black')
    ax[i].axhline(y=0.33, color='grey', linestyle='--')
    ax[i].set_xlabel(xlabel=None)

    if i/15 == 1:
        h, l = ax[i].get_legend_handles_labels()
        handles = [h[0], h[2], h[1], h[3], h[4], h[5], h[9]]
        labels = ['Button position', l[2], l[1], l[3], 'Trials', '< 100', '> 1000']
        ax[i].get_legend().remove()

    ax[i].set_title(a)
    ax[i].set_xlim([-0.5, 2.5])
    g.set(xticklabels=[], xlabel=None)
    g.set(xticklabels=[], xlabel=None, ylabel=None,
          yticks=[0, 0.33, 0.66, 1], yticklabels=['0', '.33', '.66', '1'])

ax[12].set_ylabel(ylabel='Proportion', fontsize=plot_param['labelFontSize'])
ax[12].set_xticklabels(tasks_order, rotation=90, fontsize=plot_param['labelFontSize'])
fig.tight_layout()

ax[15].legend(handles, labels, fontsize=plot_param['legendFontSize'],borderpad=0.2,
             loc='lower right', bbox_to_anchor=(1.05, -0.70), ncol=2, fancybox=True, shadow=False)

plot_name = 'Figure_3'
if plot_param['saveplot']:
    NAME = "{}{}{}".format(plot_path, plot_name, '.pdf')
    plt.savefig(NAME, format='pdf')

if plot_param['savetable']:
    NAME = "{}{}{}".format(results_path, plot_name, '.csv')
    data_model['order'] = data_model['selection'].apply(lambda x: {'static': 0, 'dynamic': 1, 'pictures': 3}[x])
    data_model = data_model.sort_values(by=['animal', 'order'], ascending=True)
    data_model = data_model[['animal', 'selection', 'estimate', 'sd', 'lower_CI', 'upper_CI']]
    data_model.to_csv(NAME, sep=';', decimal=".", index=False)

if plot_param['savetable']:
    desc_path = f"{results_path}Figure_3_description.txt"
    with open(desc_path, "w") as f:
        f.write("""
====================================================================
FIGURE 3A — Bayesian model estimates of choice proportions
====================================================================
File: Figure_3.csv

Each row corresponds to a single animal and one task condition
('static', 'dynamic', or 'pictures') derived from the Bayesian hierarchical model.

Columns:
- animal: Animal identifier.
- selection: Task condition, indicating which rule set or visual context the model refers to.
- estimate: Posterior mean of the estimated choice-proportion parameter for that condition.
- sd: Posterior standard deviation of the estimate, representing posterior uncertainty.
- lower_CI / upper_CI: Lower and upper bounds of the 95% credible interval of the posterior distribution.

Interpretation:
These parameters summarize the posterior distributions from the Bayesian model
used to estimate the probability of choosing each option type under the three task
conditions across all animals. The credible intervals quantify Bayesian uncertainty
around the posterior means.

--------------------------------------------------------------------
All numeric values are rounded to two or four decimal places as appropriate.
""")