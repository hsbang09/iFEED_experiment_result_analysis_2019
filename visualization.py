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

    def featurePrefPlot(self):
        fig, ax = plt.subplots(3, figsize=(13,18))
        general_ax, plusException_ax, parity_ax = ax

        if self.subjectGroupNames is None:
            self.subjectGroupNames = ['group_{0}'.format(i) for i in range(len(self.subjectGroups))]

        #set bar width and color range for bars (add colors as needed?..)    
        colors = ['red','blue','green','black']
        barWidth = 0.2
        
        #iterate through self.SubjectGroups
        for i, group in enumerate(self.subjectGroups):
            #iterate through group
            for count, subject in enumerate(group):
                participantId = subject.participant_id#extract subject ID, necessart?
                #get question responses for each subject
                genData = subject.feature_preference_data['generalization']  
                exceptionData = subject.feature_preference_data['generalizationPlusException']
                parityData = subject.feature_preference_data['parity']
                
            #set where on chart the bars will be    
            r1 = np.arange(len(genData)) + i*barWidth
            r2 = np.arange(len(exceptionData)) + i*barWidth
            r3 = np.arange(len(parityData)) + i*barWidth
            
            #GENERAL: plot bar chart for each subject
            general_ax.bar(r1, genData, color=colors[i], width=barWidth, edgecolor='white', label = self.subjectGroupNames[i], alpha = 0.7 )
            general_ax.legend(loc = 'upper right')
            general_ax.set_xticks([r + barWidth*i/2 for r in range(len(genData))], ['Q1', 'Q2', 'Q3'])
            
            #EXCEPTION: plots
            plusException_ax.bar(r2, exceptionData, color=colors[i], width=barWidth, edgecolor='white', label = self.subjectGroupNames[i], alpha = 0.7 )
            plusException_ax.legend(loc = 'upper right')
            plusException_ax.set_xticks([r + barWidth*i/2 for r in range(len(exceptionData))], ['Q1', 'Q2'])
    
            #PARITY: plots
            parity_ax.bar(r3, parityData, color=colors[i], width=barWidth, edgecolor='white', label = self.subjectGroupNames[i], alpha = 0.7)
            parity_ax.legend(loc = 'upper right')
            parity_ax.set_xticks([r + barWidth*i/2 for r in range(len(parityData))], ['Q1', 'Q2','Q3','Q4'])
        
    
        #set x label, y label, title, x ticks and y ticks for feature preference: generalization data
        general_ax.set_xlabel('Questions', fontweight='bold')
        general_ax.set_ylabel('Response', fontweight='bold')
        general_ax.set_title('Feature preference data: generalization', fontweight = 'bold')
        
        plusException_ax.set_xlabel('Questions', fontweight='bold')
        plusException_ax.set_ylabel('Response', fontweight='bold')
        plusException_ax.set_title('Feature preference data: generalization + exception', fontweight = 'bold')         

        parity_ax.set_xlabel('Questions', fontweight='bold')
        parity_ax.set_ylabel('Response', fontweight='bold')
        parity_ax.set_title('Feature preference data: parity', fontweight = 'bold')                             
                                 
        plt.show()
        
    def selfAssessmentPlot(self):
        fig, ax = plt.subplots(figsize=(13,6))
        selfAssessment_ax = ax

        if self.subjectGroupNames is None:
            self.subjectGroupNames = ['group_{0}'.format(i) for i in range(len(self.subjectGroups))]

        #set bar width and color range for bars (add colors?..)    
        colors = ['red','blue','green','black']
        barWidth = 0.2

        #iterate through self.SubjectGroups
        for i, group in enumerate(self.subjectGroups):
            #iterate through group
            for count, subject in enumerate(group):
                participantId = subject.participant_id#extract subject ID, necessart?
                #get question responses for each subject
                selfAssessmentData = subject.learning_self_assessment_data  
                
            #set where on chart the bars will be    
            r1 = np.arange(len(selfAssessmentData)) + i*barWidth
            
            #SELF ASSESSMENT: plot bar chart for each subject
            selfAssessment_ax.bar(r1, selfAssessmentData, color=colors[i], width=barWidth, edgecolor='white', label = self.subjectGroupNames[i], alpha = 0.7 )
            selfAssessment_ax.legend(loc = 'upper right')
            selfAssessment_ax.set_xticks([r + barWidth*i/2 for r in range(len(selfAssessmentData))], ['Q1', 'Q2', 'Q3','Q4'])

        #set x label, y label, title, x ticks and y ticks for feature preference: generalization data
        selfAssessment_ax.set_xlabel('Questions', fontweight='bold')
        selfAssessment_ax.set_ylabel('Response', fontweight='bold')
        selfAssessment_ax.set_title('Learning Self Assessment Data', fontweight = 'bold')
                        

        plt.show()
    
