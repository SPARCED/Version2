#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------- |
# CELL CYCLE BENCHMARK                                      |
# Compares to Erdem et al. Supplementary Figure 8a          |
# --------------------------------------------------------- |
# Increasing Cyclin D mRNA levels induces proper cyclin-CDK |
# complex progression and oscillations for cell cycle entry |
# and progression.                                          |
# --------------------------------------------------------- |

# Adapted from Jonah R. Huggins by Aurore K. Amrit

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# Global settings
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 14,            # default size for all text
    'axes.titlesize': 16,       # axes title size
    'axes.labelsize': 14,       # x/y label size
    'xtick.labelsize': 12,      # x tick label size
    'ytick.labelsize': 12,      # y tick label size
    'legend.fontsize': 12       # legend font size
})


# Set up a 2x2 subplot grid
fig, ax = plt.subplots(2,2, figsize=(15,5))

# Load results
cyclin_D_1 =  pd.read_csv("Cell_Cycle_step_1_cell_1.tsv", sep="\t", index_col=0)
cyclin_D_10 = pd.read_csv("Cell_Cycle_step_2_cell_1.tsv", sep="\t", index_col=0)
cyclin_D_60 = pd.read_csv("Cell_Cycle_step_3_cell_1.tsv", sep="\t", index_col=0)

# (1) Cyclin D plot
ax[0,0].plot(cyclin_D_1.index / 60, cyclin_D_1['nuc_cong__CCND__CDK4and6_'], linewidth=4, color='b')
ax[0,0].plot(cyclin_D_10.index / 60, cyclin_D_10['nuc_cong__CCND__CDK4and6_'], linewidth=4, color='r')
ax[0,0].plot(cyclin_D_60.index / 60, cyclin_D_60['nuc_cong__CCND__CDK4and6_'], linewidth=4, color='tab:orange')

ax[0,0].set_yticklabels(ax[0,0].get_yticks().astype(int), weight='bold', fontsize=16)
ax[0,0].spines[['right', 'top']].set_visible(False)
ax[0,0].set_xticklabels(ax[0,0].get_xticks().astype(int), weight='bold', fontsize=16)
ax[0,0].set_ylabel('Cyclin D (nM)', weight='bold', fontsize=20)

# (2) Cyclin E plot
ax[0,1].plot(cyclin_D_1.index / 60, cyclin_D_1['nuc_cong__CCNE__CDK2_'], linewidth=4, color='b')
ax[0,1].plot(cyclin_D_10.index / 60, cyclin_D_10['nuc_cong__CCNE__CDK2_'], linewidth=4, color='r')
ax[0,1].plot(cyclin_D_60.index / 60, cyclin_D_60['nuc_cong__CCNE__CDK2_'], linewidth=4, color='tab:orange')

ax[0,1].set_yticklabels(ax[0,1].get_yticks().astype(int), weight='bold', fontsize=16)
ax[0,1].set_xticklabels(ax[0,1].get_xticks().astype(int), weight='bold', fontsize=16)
ax[0,1].spines[['right', 'top']].set_visible(False)
ax[0,1].set_ylabel('Cyclin E (nM)', weight='bold', fontsize=20)

# (3) Cyclin A plot
ax[1,0].plot(cyclin_D_1.index / 60, cyclin_D_1['nuc_prot__CCNA__CDK2_'], linewidth=4, color='b')
ax[1,0].plot(cyclin_D_10.index / 60, cyclin_D_10['nuc_prot__CCNA__CDK2_'], linewidth=4, color='r')
ax[1,0].plot(cyclin_D_60.index / 60, cyclin_D_60['nuc_prot__CCNA__CDK2_'], linewidth=4, color='tab:orange')

ax[1,0].set_yticklabels(ax[1,0].get_yticks().astype(int), weight='bold', fontsize=16)
ax[1,0].set_xticklabels(ax[1,0].get_xticks().astype(int), weight='bold', fontsize=16)
ax[1,0].spines[['right', 'top']].set_visible(False)
ax[1,0].set_ylabel('Cyclin A (nM)', weight='bold', fontsize=20)

# (4) Cyclin B plot
ax[1,1].plot(cyclin_D_1.index / 60, cyclin_D_1['nuc_cong__CCNB__CDK1_'], linewidth=4, color='b')
ax[1,1].plot(cyclin_D_10.index / 60, cyclin_D_10['nuc_cong__CCNB__CDK1_'], linewidth=4, color='r')
ax[1,1].plot(cyclin_D_60.index / 60, cyclin_D_60['nuc_cong__CCNB__CDK1_'], linewidth=4, color='tab:orange')

ax[1,1].set_yticklabels(ax[1,1].get_yticks().astype(int), weight='bold', fontsize=16)
ax[1,1].set_xticklabels(ax[1,1].get_xticks().astype(int), weight='bold', fontsize=16)
ax[1,1].set_ylabel('Cyclin B (nM)', weight='bold', fontsize=20)
ax[1,1].spines[['right', 'top']].set_visible(False)

# Save & show
plt.tight_layout()
plt.savefig(f'./Cell-cycle.png', dpi=300, bbox_inches='tight')
plt.show()

