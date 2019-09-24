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

    def designSynthesisScatter(self, markers=None, figsize=(13,6), alpha=1.0):
        if self.subjectGroupNames is None:
            self.subjectGroupNames = ['group_{0}'.format(i) for i in range(len(self.subjectGroups))]

        if markers is None:
            markers = ['o','^','2']

        ax = None
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

            returnAxis = True
            if i == len(self.subjectGroups) - 1:
                returnAxis = False

            ax = self.drawScatter(x, y, 
                                marker=markers[i], 
                                axis=ax, 
                                xLabel="Science", 
                                yLabel="Cost", 
                                figsize=figsize, 
                                alpha=alpha, 
                                returnAxis=returnAxis)

    def featureSynthesisScatter(self, markers=None, figsize=(13,6), alpha=1.0):
        if self.subjectGroupNames is None:
            self.subjectGroupNames = ['group_{0}'.format(i) for i in range(len(self.subjectGroups))]

        if markers is None:
            markers = ['o','^','d']

        ax = None
        for i, group in enumerate(self.subjectGroups):
            x = []
            y = []

            for subject in group:
                participantId = subject.participant_id

                features = subject.feature_synthesis_task_data['features_found']
                precisions = []
                recalls = []
                for j, f in enumerate(features):
                    precisions.append(f['metrics'][2])
                    recalls.append(f['metrics'][3])

                x.append(precisions)
                y.append(recalls)

            returnAxis = True
            if i == len(self.subjectGroups) - 1:
                returnAxis = False

            ax = self.drawScatter(x, y, 
                                marker=markers[i], 
                                axis=ax, 
                                xLabel="Precision", 
                                yLabel="Recall", 
                                figsize=figsize, 
                                alpha=alpha, 
                                returnAxis=returnAxis)

    def drawScatter(self, x, y, c=None, marker=None, label=None, axis=None, xLabel=None, yLabel=None, figsize=(13,6), alpha=1.0, returnAxis=False):
        if axis is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            ax = axis

        if self.subjectGroupNames is None:
            self.subjectGroupNames = ['group_{0}'.format(i) for i in range(len(self.subjectGroups))]

        sc = ax.scatter(
                   x, 
                   y, 
                   c = c, 
                   marker = marker, 
                   cmap = "coolwarm", 
                   label = label, 
                   alpha = alpha)

        if returnAxis:
            return ax
        else:
            ax.legend(self.subjectGroupNames)
            ax.grid(True)
            ax.set_xlabel(xLabel)
            ax.set_ylabel(yLabel)
            # plt.colorbar(sc)
            plt.show()
            return None
        
