import csv
import json
import os
import numpy as np
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import math
import os
import scipy.stats as st


class Visualizer():

    def __init__(self, subjectGroups, subjectGroupNames=None):
        self.subjectGroups = subjectGroups
        self.subjectGroupNames = subjectGroupNames

    def designSynthesisScatter(self):

        fig, ax = plt.subplots(figsize=(13,6))

        if self.subjectGroupNames is None:
            self.subjectGroupNames = ['group_{0}'.format(i) for i in range(len(self.subjectGroups))]

        colors = ['red','green','blue']
        sizes = [80,80,300]
        markers = ['o','^','2']

        for i, group in enumerate(self.subjectGroups):

            x = []
            y = []

            for subject in group:
                participantId = subject.participant_id

                designs = subject.design_synthesis_task_data['designs_evaluated']
                designObjective_science = []
                designObjective_cost = []
                for j, d in enumerate(designs):
                    designObjective_science.append(d['outputs'][0])
                    designObjective_cost.append(d['outputs'][1])

                x.append(designObjective_science)
                y.append(designObjective_cost)

            sc = ax.scatter(
                       x, 
                       y, 
                       c = None, 
                       marker = markers[i], 
                       cmap = "coolwarm", 
                       label = self.subjectGroupNames[i], 
                       alpha = 1.0)

        ax.legend(self.subjectGroupNames)
        ax.grid(True)
        ax.set_xlabel('Science')
        ax.set_ylabel('Cost')
        # plt.colorbar(sc)
        plt.show()
