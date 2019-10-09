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
import seaborn as sns 

PROP_CYCLE = plt.rcParams['axes.prop_cycle']
COLORS = PROP_CYCLE.by_key()['color']

GROUP_LABEL_MAP = {
    4: "Manual",
    5: "Automated",
    6: "Interactive"
}

class Visualizer():
    def __init__(self, data=None, groups=None, groupNames=None):
        if data is not None:
            self.dataFrame = data

        elif groups is not None:
            self.groups = groups
            if groupNames is None:
                self.groupNames = ['group_{0}'.format(i) for i in range(len(self.groups))]
            else:
                self.groupNames = groupNames

            self.subjects = []
            for group in self.groups:
                for subject in group:
                    self.subjects.append(subject)

    def setDataFrame(self, data):
        self.dataFrame = data

    def simpleBoxPlot(self, columns, figsize=(10,6), grid=False, layout=None):
        fig, ax = plt.subplots(figsize=figsize)

        ax = self.dataFrame.boxplot(by=["condition"], 
                            column=columns, 
                            ax=ax,
                            grid=grid,
                            layout=layout)

    def boxPlot(self, columns, nrows=1, ncols=1, figsize=(10,6), sharex=False, sharey=False, grid=False, displayPoints=False):
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=figsize)
        grouped = self.dataFrame.groupby("condition")

        if type(columns) is not list:
            columns = [columns]

        for i, col in enumerate(columns):
            names, vals, xs = [], [] ,[]
            for j, (name, subdf) in enumerate(grouped):
                names.append(GROUP_LABEL_MAP[name])
                vals.append(subdf[col].tolist())
                xs.append(np.random.normal(j+1, 0.04, subdf.shape[0]))

            ax[i].boxplot(vals, labels=names)
            ngroup = len(vals)
            clevels = np.linspace(0., 1., ngroup)
            ax[i].set_title(col)

            for x, val, clevel in zip(xs, vals, clevels):
                ax[i].scatter(x, val, alpha=0.4)

    def parallelCoordinates(self, columns, figsize=(13,6), colors=None, legend=None, grid=False):
        fig, ax = plt.subplots(figsize=figsize)

        if colors is None:
            colors = []
            for i in range(10):
                colors.append(COLORS[i])

        if columns is None:
            columns = ['fcl','fpwc', 'dcl','dpwc','FScore','DScore','PScore','NScore','totalScore']

        pd.plotting.parallel_coordinates(frame=self.dataFrame, 
                class_column='condition', 
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

        self.subjects = []
        for group in self.groups:
            for subject in group:
                self.subjects.append(subject)

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

            ax = self.scatterPlot(x, y, 
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

            ax = self.scatterPlot(x, y, 
                                marker=markers[i], 
                                legend=self.groupNames,
                                axis=ax, 
                                xLabel="Precision", 
                                yLabel="Recall", 
                                figsize=figsize, 
                                alpha=alpha, 
                                returnAxis=returnAxis)

    def scatterPlot(self, x, y, c=None, marker=None, legend=None, label=None, axis=None, xLabel=None, yLabel=None, figsize=(13,6), alpha=1.0, returnAxis=False):
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

    def barChart(self, data, groupNames, ax=None, axisIndex=None, xLabel=None, yLabel=None, title=None, colors=None, barWidth=0.2, nrows=1, ncols=1, figsize=(10,6), sharex=False, sharey=False):
        if ax is None:
            fig, ax = plt.subplots(nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=figsize)

            if type(ax) is list and axisIndex is None:
                axisIndex = 0
        
        #set bar width and color range for bars (add colors as needed?..)    
        if colors is None:
            colors = []
            for i in range(10):
                colors.append(COLORS[i])

        if axisIndex is None:
            if type(ax) is list:
                thisAxis = ax[0]
            else:
                thisAxis = ax
        else:
            thisAxis = ax[axisIndex]

        # transpose the data
        Tdata = np.array(data).transpose()

        for gIndex, groupData in enumerate(Tdata):
            #set where on chart the bars will be    
            r1 = np.arange(len(groupData)) + gIndex * barWidth
            
            #GENERAL: plot bar chart for each subject
            thisAxis.bar(r1, groupData, color=colors[gIndex], width=barWidth, edgecolor='white', label=groupNames[gIndex], alpha=0.7)
            thisAxis.legend(loc='upper right')
            thisAxis.set_xticks([r + barWidth * i / 2 for r in range(len(groupData))], ['Q1', 'Q2', 'Q3'])
        
        #set x label, y label, title, x ticks and y ticks for feature preference: generalization data
        if xLabel is not None:
            thisAxis.set_xlabel(xLabel)
        if yLabel is not None: 
            thisAxis.set_ylabel(yLabel)
        if title is not None:
            thisAxis.set_title(title)

    def featurePrefPlot(self, barWidth=0.2, figsize=(13,18), colors=None):
        fig, ax = plt.subplots(3, figsize=figsize)

        # iterate through all subjects
        answerCounter = [[0,0],[0,0],[0,0]]
        for i, subject in enumerate(self.subjects):
            data = subject.feature_preference_data['generalization']
            for qInd, ans in enumerate(data):
                if ans == 1:
                    answerCounter[qInd][0] += 1
                else:
                    answerCounter[qInd][1] += 1
        self.barChart(data=answerCounter, groupNames=["HighLevel","LowLevel"], ax=ax, axisIndex=0, colors=colors, xLabel="Questions", yLabel="Response", title="Feature preference data: generalization")

        # iterate through all subjects
        answerCounter = [[0,0],[0,0],[0,0]]
        for i, subject in enumerate(self.subjects):
            data = subject.feature_preference_data['generalizationPlusException']
            for qInd, ans in enumerate(data):
                if ans == 1:
                    answerCounter[qInd][0] += 1
                else:
                    answerCounter[qInd][1] += 1
        self.barChart(data=answerCounter, groupNames=["Gen+Exception","LowLevel"], ax=ax, axisIndex=1, colors=colors, xLabel="Questions", yLabel="Response", title="Feature preference data: generalization + exception")

        # iterate through all subjects
        answerCounter = [[0,0],[0,0],[0,0]]
        for i, subject in enumerate(self.subjects):
            data = subject.feature_preference_data['parity']
            for qInd, ans in enumerate(data):
                if qInd == 0 or qInd == 2:
                    if ans == 1:
                        answerCounter[qInd][1] += 1
                    else:
                        answerCounter[qInd][0] += 1
                else:
                    if ans == 1:
                        answerCounter[qInd][0] += 1
                    else:
                        answerCounter[qInd][1] += 1
        self.barChart(data=answerCounter, groupNames=["Positive","Negative"], ax=ax, axisIndex=2, colors=colors, xLabel="Questions", yLabel="Response", title="Feature preference data: parity")
        plt.show()
        
    def selfAssessmentPlot(self, barWidth=0.2, colors=None, figsize=(13,6)):
        fig, ax = plt.subplots(figsize=figsize)

        averagedDataPerGroup = [] # [[0,0,0,0], [0,0,0,0], [0,0,0,0]]

        # iterate through self.SubjectGroups
        for i, group in enumerate(self.groups):
            # iterate through group
            accumulatedData = []
            for count, subject in enumerate(group):
                # get question responses for each subject
                if len(accumulatedData) == 0:
                    accumulatedData = subject.learning_self_assessment_data
                else:
                    accumulatedData = [accumulatedData[a] + subject.learning_self_assessment_data[a] for a in range(len(accumulatedData))]
            
            # Take the average
            averagedData = [accumulatedData[a] / len(group) for a in range(len(accumulatedData))]
            averagedDataPerGroup.append(averagedData)
            
        averagedDataPerGroup = np.array(averagedDataPerGroup).transpose()
        self.barChart(averagedDataPerGroup, groupNames=self.groupNames, ax=ax, axisIndex=None, xLabel="Questions", yLabel="Response", title="Learning Self Assessment Data", colors=colors, barWidth=barWidth, figsize=figsize)
        plt.show()
    
