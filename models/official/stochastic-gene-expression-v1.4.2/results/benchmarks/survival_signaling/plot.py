#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------- |
# SURVIVAL SIGNALING BENCHMARK                              |
# Compares to Erdem et al. Supplementary Figure 7d          |
# --------------------------------------------------------- |
# Increasing ERK and AKT activity levels prolongs TRAIL     |
# induced time to death, whereas increasing PUMA and NOXA   |
# expression levels decreases the time it takes for cells   |
# to die.                                                   |
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


# Set up figure size
plt.figure(figsize=(7, 4))

# Load results
TRAIL_only =  pd.read_csv("Survival_Signaling_step_1_cell_1.tsv", sep="\t", index_col=0)
TRAIL_ERK_AKT = pd.read_csv("Survival_Signaling_step_2_cell_1.tsv", sep="\t", index_col=0)
TRAIL_PUMA_NOXA = pd.read_csv("Survival_Signaling_step_3_cell_1.tsv", sep="\t", index_col=0)

# Plot
plt.plot(TRAIL_only.index / 125, 
         TRAIL_only['cyt_prot__cl_PARP1_1_'],
         label='TRAIL only', linewidth=4, color='black')
plt.plot(TRAIL_ERK_AKT.index / 125, 
         TRAIL_ERK_AKT['cyt_prot__cl_PARP1_1_'],
         label='+ppERK/+ppAKT', linewidth=4, color='blue')
plt.plot(TRAIL_PUMA_NOXA.index / 125, 
         TRAIL_PUMA_NOXA['cyt_prot__cl_PARP1_1_'],
         label='+PUMA/+NOXA', linewidth=4, color='red')

plt.xlabel('Time (hr)', fontsize=20, weight='bold')
plt.ylabel('cPARP (nM)', fontsize=20, weight='bold')
plt.grid(True)
plt.xlim(0, 50)
plt.ylim(0, 400)
plt.xticks(fontsize=16, weight='bold')
plt.yticks(fontsize=16, weight='bold')
plt.legend(['Low TRAIL dose','+ppERK / +ppAKT','+PUMA / +NOXA'], bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False)

# Save & show
plt.tight_layout()
plt.savefig(f'./Survival-signaling.png', dpi=300)
plt.show()

