#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------- |
# DNA REPAIR BENCHMARK                                      |
# Compares to Erdem et al. Supplementary Figure 6a          |
# --------------------------------------------------------- |
# Single and/or double stranded DNA damage activates p53,   |
# while DNA damage repair mechanisms represses its response |
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

# Set up a 3x1 subplot grid
fig, axs = plt.subplots(3, 1, figsize=(6, 6), sharex=True)

# --- helper to style ticks ---
def style_ticks(ax, axis="both"):
    ax.tick_params(axis=axis, labelsize=14)
    if axis in ["y", "both"]:
        for label in ax.get_yticklabels():
            label.set_fontweight("bold")
    if axis in ["x", "both"]:
        for label in ax.get_xticklabels():
            label.set_fontweight("bold")

# (1) Plot single stranded break results
single_without_repair = pd.read_csv("DNA_repair_step_1_cell_1.tsv", sep="\t", index_col=0)
single_with_repair =    pd.read_csv("DNA_repair_step_2_cell_1.tsv", sep="\t", index_col=0)

axs[0].plot(single_without_repair.index,
            single_without_repair["nuc_prot_a__P53_"],
            label='Without Repair', color='blue', linewidth=4)
axs[0].plot(single_with_repair.index,
            single_with_repair["nuc_prot_a__P53_"],
            label='With Repair', color='red', linewidth=4)
            
axs[0].grid(True)
axs[0].set_ylim(0, 400)
axs[0].set_xticks(np.arange(0, 24, step=6))
axs[0].legend(frameon=False)
axs[0].text(12.50, 350.0, 'Single Stranded DNA damage', fontsize=12)
style_ticks(axs[0])

# (2) Plot double stranded break results
double_without_repair = pd.read_csv("DNA_repair_step_3_cell_1.tsv", sep="\t", index_col=0)
double_with_repair =    pd.read_csv("DNA_repair_step_4_cell_1.tsv", sep="\t", index_col=0)

axs[1].plot(double_without_repair.index,
            double_without_repair["nuc_prot_a__P53_"],
            label='Without Repair', color='blue', linewidth=4)
axs[1].plot(double_with_repair.index,
            double_with_repair["nuc_prot_a__P53_"],
            label='With Repair', color='red', linewidth=4)

axs[1].grid(True)
axs[1].set_xticks(np.arange(0, 24, step=6))
axs[1].set_ylim(0, 1000)
axs[1].text(12.50, 900.0, 'Double Stranded DNA damage', fontsize=12)
style_ticks(axs[1])

# (3) Single and double stranded breaks results
single_and_double_without_repair = pd.read_csv("DNA_repair_step_5_cell_1.tsv", sep="\t", index_col=0)
single_and_double_with_repair =    pd.read_csv("DNA_repair_step_6_cell_1.tsv", sep="\t", index_col=0)

axs[2].plot(single_and_double_without_repair.index,
            single_and_double_without_repair["nuc_prot_a__P53_"],
            label='Without Repair', color='blue', linewidth=4)
axs[2].plot(single_and_double_with_repair.index,
            single_and_double_with_repair["nuc_prot_a__P53_"],
            label='With Repair', color='red', linewidth=4)

axs[2].grid(True)
axs[2].set_ylim(0, 1200)
axs[2].text(15.0, 900.0, 'DS + SS DNA damage', fontsize=12)
axs[2].set_xlabel('Time (hrs)', weight='bold', fontsize=20)
style_ticks(axs[2], axis="both")

# Set the y-axis label (shared)
fig.text(-0.05, 0.5, 'Active p53 (nM)', va='center',
         rotation='vertical', weight='bold', fontsize=20)

plt.tight_layout()
plt.savefig(f'./DNA-repair.png', dpi=300, bbox_inches='tight')
plt.show()

