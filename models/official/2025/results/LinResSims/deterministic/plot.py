#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd


drug = input("Enter drug name: ")

# Load experiment
drug_incub = pd.read_csv(f"{drug}_step_1_cell_1.tsv", sep="\t", index_col=0)
drug_simul = pd.read_csv(f"{drug}_step_2_cell_1.tsv", sep="\t", index_col=0)
# Compute time continuity
incubation_t = drug_incub["time"].iloc[-1]
drug_simul["time"] += incubation_t
# Merge
experiment = pd.concat([drug_incub, drug_simul], ignore_index=True)
last_time = experiment["time"].iloc[-1]
# Load control
control_incub = pd.read_csv("control_step_1_cell_1.tsv", sep="\t", index_col=0)
control_simul = pd.read_csv("control_step_3_cell_1.tsv", sep="\t", index_col=0)     # WARNING: edit step consistently
control_simul["time"] += incubation_t
control = pd.concat([control_incub, control_simul], ignore_index=True)
control = control[control["time"] <= last_time]

plot_loop = True
matplotlib.rcParams['font.sans-serif'] = ['arial']
font_param = {'family':'arial', 'size':15}
while plot_loop:
    compound = input("Enter compound: ")
    if compound != "STOP":
        fig = plt.figure(figsize=(8, 5), dpi=300, facecolor='w', edgecolor='k')
        plt.plot(control["time"] / 3600, control[compound], 'b', linewidth=3, label="Control")
        plt.plot(experiment["time"] / 3600, experiment[compound], 'r', linewidth=3, label=drug.capitalize())
        plt.axvline(incubation_t / 3600, color='g')
        plt.xlim([-0.5, (last_time / 3600)+1])
        plt.legend()
        plt.ylabel('Concentration (nM)', fontdict = font_param)
        plt.xlabel('Time (hours)', fontdict = font_param)
        plt.title(compound, fontdict = font_param)
        plt.xticks(np.arange(0, (last_time/3600)+1, step=2), fontsize=15)
        plt.yticks(fontsize=15)
        plt.show()
        plt.savefig(f"plots/{drug}_{compound}", format='png', bbox_inches='tight')
    else:
        plot_loop = False

