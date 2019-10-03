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

    def __init__(self, data=None, groups=None, groupNames=None):
        if data is not None:
            self.data = data

        elif groups is not None:
            self.groups = groups
            if groupNames is None:
                self.groupNames = ['group_{0}'.format(i) for i in range(len(self.groups))]
            else:
                self.groupNames = groupNames

    def setDataFrame(self, data):
        self.data = data

    def boxPlot(self, columns, figsize=(10,6), grid=False, layout=None):
        fig, ax = plt.subplots(figsize=figsize)

        ax = self.data.boxplot(by=["condition"], 
                            column=columns, 
                            ax=ax,
                            grid=grid,
                            layout=layout)

    def parallelCoordinates(self, columns, figsize=(13,6), colors=None, legend=None, grid=False):

        fig, ax = plt.subplots(figsize=figsize)

        # if colors is None:
        #     colors = ['#556270', '#4ECDC4', '#C7F464']

        if columns is None:
            columns = ['fcl','fpwc', 'dcl','dpwc','FScore','DScore','PScore','NScore','totalScore']

        pd.plotting.parallel_coordinates(self.data, 'condition', 
                ax=ax,
                cols=columns,
                color=colors)

        if legend is not None:
            ax.legend(legend)
        ax.grid(grid)
        # ax.set_xlabel(xLabel)
        # ax.set_ylabel(yLabel)
        # plt.colorbar(sc)
        plt.show()

    def setSubjectGroups(self, groups, groupNames=None):
        self.groups = groups
        if groupNames is None:
            self.groupNames = ['group_{0}'.format(i) for i in range(len(self.groups))]
        else:
            self.groupNames = groupNames

    def designSynthesisScatter(self, markers=None, figsize=(13,6), alpha=1.0):
        if self.groups is None:
            raise ValueError("")

        if markers is None:
            markers = ['o','^','2']

        ax = None
        for i, group in enumerate(self.groups):
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

                x += designObjective_science
                y += designObjective_cost

            returnAxis = True
            if i == len(self.groups) - 1:
                returnAxis = False

            ax = self.drawScatter(x, y, 
                                marker=markers[i], 
                                legend=self.groupNames,
                                axis=ax, 
                                xLabel="Science", 
                                yLabel="Cost", 
                                figsize=figsize, 
                                alpha=alpha, 
                                returnAxis=returnAxis)

    def featureSynthesisScatter(self, useLearningTaskData=False, markers=None, figsize=(13,6), alpha=1.0):
        if self.groups is None:
            raise ValueError("")

        if markers is None:
            markers = ['o','^','d']

        ax = None
        for i, group in enumerate(self.groups):
            x = []
            y = []

            for subject in group:
                participantId = subject.participant_id

                if useLearningTaskData:
                    features = subject.learning_task_data['features_found']
                else:
                    features = subject.feature_synthesis_task_data['features_found']
                precisions = []
                recalls = []
                for j, f in enumerate(features):
                    precisions.append(f['metrics'][2])
                    recalls.append(f['metrics'][3])

                x += precisions
                y += recalls

            returnAxis = True
            if i == len(self.groups) - 1:
                returnAxis = False

            ax = self.drawScatter(x, y, 
                                marker=markers[i], 
                                legend=self.groupNames,
                                axis=ax, 
                                xLabel="Precision", 
                                yLabel="Recall", 
                                figsize=figsize, 
                                alpha=alpha, 
                                returnAxis=returnAxis)

    def drawScatter(self, x, y, c=None, marker=None, legend=None, label=None, axis=None, xLabel=None, yLabel=None, figsize=(13,6), alpha=1.0, returnAxis=False):
        if axis is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            ax = axis

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
            ax.legend(legend)
            ax.grid(True)
            ax.set_xlabel(xLabel)
            ax.set_ylabel(yLabel)
            # plt.colorbar(sc)
            plt.show()
            return None
        
