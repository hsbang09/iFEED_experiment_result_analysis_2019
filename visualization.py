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
from scipy import stats
import seaborn as sns 

PROP_CYCLE = plt.rcParams['axes.prop_cycle']
COLORS = PROP_CYCLE.by_key()['color']

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

    def boxPlot(self, columns, conditions=None, nrows=1, ncols=1, figsize=(10,6), sharex=False, sharey=False, grid=False, displayPoints=False, dataFrame=None):
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=figsize)

        if dataFrame is None:
            dataFrame = self.dataFrame

        if conditions is None:
            conds = dataFrame["condition"].values
            naming1 = ["manual", "automated", "interactive"]
            naming2 = ["MKE", "AKE", "IKE"]
            if conds[0] in naming1:
                conditions = naming1
            elif conds[0] in naming2:
                conditions = naming2

        grouped = dataFrame.groupby("condition")

        groupedReordered = []
        for targetName in conditions:
            for (name, subdf) in grouped:
                if name == targetName:
                    groupedReordered.append((name, subdf))
        grouped = groupedReordered

        if type(columns) is not list:
            columns = [columns]

        for i, col in enumerate(columns):
            names, vals, xs = [], [] ,[]
            for j, (name, subdf) in enumerate(grouped):
                names.append(name)
                vals.append(subdf[col].tolist())
                xs.append(np.random.normal(j+1, 0.04, subdf.shape[0]))

            ax[i].boxplot(vals, labels=names)
            ngroup = len(vals)
            clevels = np.linspace(0., 1., ngroup)
            ax[i].set_title(col)

            for x, val, clevel in zip(xs, vals, clevels):
                ax[i].scatter(x, val, alpha=0.4)

    def parallelCoordinateVariablePairs(self, varPairList=None, nrows=1, ncols=1, sharex=False, sharey=False, colors=None, figsize=(10,6), removeLegend=False, grid=False, groupBy="condition", dataFrame=None, **kwds):
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=figsize)

        if dataFrame is None:
            dataFrame = self.dataFrame

        for i, varPair in enumerate(varPairList):
            self.parallelCoordinates(columns=varPair, axis=ax[i], figsize=None, colors=colors, grid=grid, groupBy=groupBy, removeLegend=removeLegend, dataFrame=dataFrame, **kwds)
        plt.show()

    def parallelCoordinates(self, columns, axis=None, figsize=(13,6), colors=None, grid=False, dataFrame=None, removeLegend=False, groupBy="condition", **kwds):
        if axis is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            ax = axis

        collapseGroups = False

        if dataFrame is None:
            dataFrame = self.dataFrame

        if colors is None:
            colors = []
            for i in range(10):
                colors.append(COLORS[i])

        if columns is None:
            columns = ['fcl','fpwc', 'dcl','dpwc','FScore','DScore','PScore','NScore','totalScore']

        if groupBy is None:
            groupBy = "condition"
            colors = [colors[0]] * 10
            collapseGroups = True

        pd.plotting.parallel_coordinates(frame=dataFrame, 
                class_column=groupBy, 
                ax=ax,
                cols=columns,
                color=colors,
                **kwds)

        ax.grid(grid)
        if collapseGroups or removeLegend:
            ax.get_legend().remove()

        if axis is None:
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

    def designSynthesisScatterDF(self, dataFrame, 
                cColumn=None, 
                useDesignNum=False, targetDesignFilePath=None, 
                targetDesignAlpha=1.0, targetDesignColor=None, targetDesignMarker='o',
                cmap="Blues", figsize=(13,6), alpha=1.0, colorbar=True):

        x = []
        y = []
        c = []

        df = dataFrame
        for s in self.subjects:
            designs = s.design_synthesis_task_data['designs_evaluated']
            designObjective_science = []
            designObjective_cost = []
            for j, d in enumerate(designs):
                designObjective_science.append(d['outputs'][0])
                designObjective_cost.append(d['outputs'][1])
            x += designObjective_science
            y += designObjective_cost

            if useDesignNum:
                for i in range(len(designObjective_science)):
                    c.append(i)

            elif cColumn is not None:
                for i in range(len(designObjective_science)):
                    c.append(df.loc[df.id == s.participant_id][cColumn].values[0])

        returnAxis = False
        if targetDesignFilePath:
            returnAxis = True

        ax = self.scatterPlot(x, y, 
                            c=c,
                            marker='o', 
                            legend=None,
                            xLabel="Science", 
                            yLabel="Cost", 
                            figsize=figsize, 
                            alpha=alpha, 
                            cmap=cmap,
                            returnAxis=returnAxis,
                            colorbar=colorbar)

        if targetDesignFilePath:
            indexTotal = []
            classLabel = []
            scienceTotal = []
            costTotal = []

            # load in csv
            with open(targetDesignFilePath) as csvfile:
                readCSV = csv.reader(csvfile, delimiter = ',')

                for row in readCSV:
                    index = row[0]
                    targetVal = row[1]
                    science = row[3]
                    cost = row[4]
                    indexTotal.append(int(index))
                    classLabel.append(int(targetVal))
                    scienceTotal.append(float(science))
                    costTotal.append(float(cost))

            # initialize empty arrays
            targetScience = []
            targetCost = []
            numTargetDesigns = 0

            # iterate through the column that contains a 0 or 1 describing if 
            # design is a target. if Yes (targetbool = 1), append science and cost
            # to array
            for i, label in enumerate(classLabel):
                if label == 1:
                    targetScience.append(scienceTotal[i])
                    targetCost.append(costTotal[i])
            numTargetDesigns = len(targetScience)

            ax = self.scatterPlot(targetScience, targetCost, 
                    c=targetDesignColor,
                    axis=ax,
                    marker=targetDesignMarker, 
                    legend=None,
                    xLabel="Science", 
                    yLabel="Cost", 
                    figsize=figsize, 
                    alpha=targetDesignAlpha, 
                    cmap=cmap,
                    returnAxis=False,
                    colorbar=False)

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

    def featureSynthesisScatterDF(self, dataFrame, useLearningTaskData=False, cColumn=None, cmap="Blues", figsize=(13,6), alpha=1.0, colorbar=True):
        x = []
        y = []
        c = []

        df = dataFrame
        for s in self.subjects:
            if useLearningTaskData:
                features = s.learning_task_data['features_found']
            else:
                features = s.feature_synthesis_task_data['features_found']
            precisions = []
            recalls = []
            for j, f in enumerate(features):
                precisions.append(f['metrics'][2])
                recalls.append(f['metrics'][3])

            x += precisions
            y += recalls
            if cColumn is not None:
                for i in range(len(precisions)):
                    c.append(df.loc[df.id == s.participant_id][cColumn].values[0])

        ax = self.scatterPlot(x, y, 
                            c=c,
                            marker='o', 
                            legend=None,
                            xLabel="Precision", 
                            yLabel="Recall", 
                            figsize=figsize, 
                            alpha=alpha, 
                            cmap=cmap,
                            returnAxis=False,
                            colorbar=colorbar)

    def scatterPlot(self, x, y, s=None, c=None, cmap="coolwarm", marker=None, legend=None, label=None, axis=None, xLabel=None, yLabel=None, figsize=(13,6), alpha=1.0, grid=False, returnAxis=False, colorbar=False):
        if axis is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            ax = axis

        sc = ax.scatter(
                   x, 
                   y, 
                   s=s,
                   c=c, 
                   marker=marker, 
                   cmap=cmap, 
                   label=label, 
                   alpha=alpha)

        if colorbar:
            plt.colorbar(sc)

        if returnAxis:
            return ax
        else:
            if legend:
                ax.legend(legend)
            ax.grid(grid)

            if xLabel:
                ax.set_xlabel(xLabel)
            if yLabel:
                ax.set_ylabel(yLabel)
            plt.show()
            return None

    def linePlot(self, x, y, c=None, axis=None, linestyle=None, figsize=(13,6), xLabel=None, yLabel=None, legend=None, grid=False, returnAxis=False):
        if axis is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            ax = axis

        ax.plot(
           x, 
           y, 
           c=c, 
           linestyle=linestyle)

        if returnAxis:
            return ax
        else:
            ax.legend(legend)
            ax.grid(True)

            if xLabel:
                ax.set_xlabel(xLabel)
            if yLabel:
                ax.set_ylabel(yLabel)
            plt.show()
            return None

    def designSynthesisLinePlot(self, 
                subjects=None,
                subjectGroups=None,
                subjectGroupNames=None,
                conditions=None,
                figsize=(13,6), 
                alpha=1.0, 
                colors=None,
                linestyles=None,):

        if colors is None:
            colors = []
            for i in range(10):
                colors.append(COLORS[i])

        if linestyles is None:
            linestyles = ['-'] * 10

        # initialize groups
        groups = []
        groupNames = []
        if subjects is not None:
            for s in subjects:
                groups.append([s])
                groupNames.append([s.participant_id])

        elif subjectGroups is not None:
            if subjectGroupNames is None:
                raise ValueError("")
            groups = subjectGroups
            groupNames = subjectGroupNames

        else:
            groups = self.groups
            groupNames = self.groupNames

        ax = None
        for i, group in enumerate(groups):
            for j, subject in enumerate(group):
                # designs = subject.design_synthesis_task_data['designs_evaluated']
                # x = []
                # y = []
                # for j, d in enumerate(designs):
                #     x.append(d['outputs'][0]) # science
                #     y.append(d['outputs'][1]) # cost

                y = subject.design_synthesis_task_data["minDistList"]
                x = [index + 1 for index in range(len(y))]

                returnAxis = True
                if i == len(groups) - 1 and j == len(group) - 1:
                    returnAxis = False

                ax = self.linePlot(x, y, 
                                    c=colors[i], 
                                    linestyle=linestyles[i],
                                    legend=groupNames,
                                    axis=ax, 
                                    xLabel="Trials", 
                                    yLabel="Distance to target", 
                                    figsize=figsize, 
                                    # alpha=alpha, 
                                    returnAxis=returnAxis)

    def barplot_annotate_brackets(self, num1, num2, data, center, height, yerr=None, dh=.05, barh=.05, fs=None, maxasterix=None):
        """ Source: https://stackoverflow.com/questions/11517986/indicating-the-statistically-significant-difference-in-bar-graph

        Annotate barplot with p-values.

        :param num1: number of left bar to put bracket over
        :param num2: number of right bar to put bracket over
        :param data: string to write or number for generating asterixes
        :param center: centers of all bars (like plt.bar() input)
        :param height: heights of all bars (like plt.bar() input)
        :param yerr: yerrs of all bars (like plt.bar() input)
        :param dh: height offset over bar / bar + yerr in axes coordinates (0 to 1)
        :param barh: bar height in axes coordinates (0 to 1)
        :param fs: font size
        :param maxasterix: maximum number of asterixes to write (for very small p-values)


        Usage example:
            heights = [1.8, 2, 3]
            bars = np.arange(len(heights))
            plt.figure()
            plt.bar(bars, heights, align='center')
            plt.ylim(0, 5)
            barplot_annotate_brackets(0, 1, .1, bars, heights)
            barplot_annotate_brackets(1, 2, .001, bars, heights)
            barplot_annotate_brackets(0, 2, 'p < 0.0075', bars, heights, dh=.2)
        """

        if type(data) is str:
            text = data
        else:
            # * is p < 0.05
            # ** is p < 0.005
            # *** is p < 0.0005
            # etc.
            text = ''
            p = .05

            while data < p:
                text += '*'
                p /= 10.

                if maxasterix and len(text) == maxasterix:
                    break

            if len(text) == 0:
                text = 'n. s.'

        lx, ly = center[num1], height[num1]
        rx, ry = center[num2], height[num2]

        if yerr:
            ly += yerr[num1]
            ry += yerr[num2]

        ax_y0, ax_y1 = plt.gca().get_ylim()
        dh *= (ax_y1 - ax_y0)
        barh *= (ax_y1 - ax_y0)

        y = max(ly, ry) + dh

        barx = [lx, lx, rx, rx]
        bary = [y, y+barh, y+barh, y]
        mid = ((lx+rx)/2, y+barh)

        plt.plot(barx, bary, c='black')

        kwargs = dict(ha='center', va='bottom')
        if fs is not None:
            kwargs['fontsize'] = fs

        plt.text(*mid, text, **kwargs)

    def barPlot(self, columns=None, 
                    conditions=None, 
                    showError=False, 
                    nrows=1, ncols=1, 
                    figsize=(10,6), 
                    width=0.8, 
                    sharex=False, 
                    sharey=False, 
                    grid=False, 
                    title=None, 
                    displayPoints=False, 
                    dataFrame=None, 
                    subplotsAdjust=None, 
                    subplotsHide=None, 
                    tightLayout=False):

        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=figsize)

        if tightLayout:
            fig.tight_layout()

        if len(np.shape(ax)) == 1: # 1D
            pass
        elif len(np.shape(ax)) == 2: # 2D
            ax = ax.flatten()

        if dataFrame is None:
            dataFrame = self.dataFrame

        if conditions is None:
            conds = dataFrame["condition"].values
            naming1 = ["manual", "automated", "interactive"]
            naming2 = ["MKE", "AKE", "IKE"]
            if conds[0] in naming1:
                conditions = naming1
            elif conds[0] in naming2:
                conditions = naming2

        grouped = dataFrame.groupby("condition")

        groupedReordered = []
        for targetName in conditions:
            for (name, subdf) in grouped:
                if name == targetName:
                    groupedReordered.append((name, subdf))
        grouped = groupedReordered

        if type(columns) is not list:
            columns = [columns]

        for i, col in enumerate(columns):
            names, vals, xs = [], [] ,[]
            for j, (name, subdf) in enumerate(grouped):
                names.append(name)
                vals.append(subdf[col].tolist())

                tempX = np.random.normal(j+1, 0.06, subdf.shape[0])
                tempXOffset = []
                for x in tempX:
                    if np.random.randint(2) == 1:
                        x += 0.15
                    else:
                        x -= 0.15
                    tempXOffset.append(x)
                xs.append(tempXOffset)

            if showError:
                stdErr = [stats.sem(val) for val in vals]
                capsize = 10
            else:
                stdErr = None
                capsize = None

            x_pos = np.arange(len(conditions))
            x_pos = [x + 1 for x in x_pos]
            heights = [np.mean(val) for val in vals]

            ax[i].bar(x_pos, heights, yerr=stdErr, capsize=capsize, width=width, color="white", edgecolor="black", align='center', alpha=1.0, zorder=0)
            ax[i].set_xticks(x_pos)
            ax[i].set_xticklabels(conditions)

            ngroup = len(vals)
            clevels = np.linspace(0., 1., ngroup)
            ax[i].set_title(col)

            if displayPoints:
                for x, val, clevel in zip(xs, vals, clevels):
                    ax[i].scatter(x, val, color="black", alpha=0.5, zorder=1)
        
        if title is not None:
            plt.title(title)

        if subplotsAdjust is not None:
            plt.subplots_adjust(**subplotsAdjust)
            # left  = 0.125  # the left side of the subplots of the figure
            # right = 0.9    # the right side of the subplots of the figure
            # bottom = 0.1   # the bottom of the subplots of the figure
            # top = 0.9      # the top of the subplots of the figure
            # wspace = 0.2   # the amount of width reserved for blank space between subplots
            # hspace = 0.2   # the amount of height reserved for white space between subplots

        if subplotsHide is not None:
            for index in subplotsHide:
                ax[index].axis('off')
        plt.show()

    def barPlotSingle(self, columns=None, 
                    conditions=None, 
                    showError=False, 
                    figsize=(10,6), 
                    width=0.8, 
                    grid=False, 
                    title=None, 
                    displayPoints=False, 
                    dataFrame=None,
                    returnAxis=False,
                    axis=None,
                    columnAlias=None):
        
        if axis is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            ax = axis

        if dataFrame is None:
            dataFrame = self.dataFrame

        if type(columns) is not list:
            columns = [columns]

        names, vals, xs = [], [] ,[]
        if columnAlias:
            names = columnAlias
        else:
            names = columns

        for i, col in enumerate(columns):
            vals.append(dataFrame[col].tolist())

            tempX = np.random.normal(i+1, 0.06, dataFrame.shape[0])
            tempXOffset = []
            for x in tempX:
                if np.random.randint(2) == 1:
                    x += 0.15
                else:
                    x -= 0.15
                tempXOffset.append(x)
            xs.append(tempXOffset)

        if showError:
            stdErr = [stats.sem(val) for val in vals]
            capsize = 10
        else:
            stdErr = None
            capsize = None

        x_pos = np.arange(len(columns))
        x_pos = [x + 1 for x in x_pos]
        heights = [np.mean(val) for val in vals]

        ax.bar(x_pos, heights, yerr=stdErr, capsize=capsize, width=width, color="white", edgecolor="black", align='center', alpha=1.0, zorder=0)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(names)

        ngroup = len(vals)
        clevels = np.linspace(0., 1., ngroup)
        
        if displayPoints:
            for x, val, clevel in zip(xs, vals, clevels):
                ax.scatter(x, val, color="black", alpha=0.5, zorder=1)
        
        if title is not None:
            ax.set_title(title)
            # plt.title(title)

        if returnAxis:
            return ax
        else:
            plt.show()

    def catBarPlot(self, data, groupNames, errData=None, ax=None, axisIndex=None, xLabel=None, yLabel=None, title=None, colors=None, barWidth=0.2, nrows=1, ncols=1, figsize=(10,6), sharex=False, sharey=False):
        # Categorical data

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
        if errData is not None:
            Terr = np.array(errData).transpose()

        for gIndex, groupData in enumerate(Tdata):
            #set where on chart the bars will be    
            r1 = np.arange(len(groupData)) + gIndex * barWidth
            
            #GENERAL: plot bar chart for each subject
            yerr = None
            if errData is not None:
                yerr = Terr[gIndex]

            thisAxis.bar(r1, groupData, yerr=yerr, color=colors[gIndex], width=barWidth, edgecolor='white', label=groupNames[gIndex], alpha=0.7)
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
        self.catBarPlot(data=answerCounter, groupNames=["HighLevel","LowLevel"], ax=ax, axisIndex=0, colors=colors, xLabel="Questions", yLabel="Response", title="Feature preference data: generalization")

        # iterate through all subjects
        answerCounter = [[0,0],[0,0],[0,0]]
        for i, subject in enumerate(self.subjects):
            data = subject.feature_preference_data['generalizationPlusException']
            for qInd, ans in enumerate(data):
                if ans == 1:
                    answerCounter[qInd][0] += 1
                else:
                    answerCounter[qInd][1] += 1
        self.catBarPlot(data=answerCounter, groupNames=["Gen+Exception","LowLevel"], ax=ax, axisIndex=1, colors=colors, xLabel="Questions", yLabel="Response", title="Feature preference data: generalization + exception")

        # iterate through all subjects
        answerCounter = [[0,0],[0,0],[0,0]]
        for i, subject in enumerate(self.subjects):
            data = subject.feature_preference_data['parity']
            for qInd, ans in enumerate(data):
                if qInd == 0 or qInd == 2:
                    if ans == 1:
                        answerCounter[qInd][1] += 1
                    else: # ans == 2
                        answerCounter[qInd][0] += 1
                else:
                    if ans == 1:
                        answerCounter[qInd][0] += 1
                    else: # ans == 2
                        answerCounter[qInd][1] += 1
        self.catBarPlot(data=answerCounter, groupNames=["Positive","Negative"], ax=ax, axisIndex=2, colors=colors, xLabel="Questions", yLabel="Response", title="Feature preference data: parity")
        plt.show()
        
    def selfAssessmentPlot(self, displayStderr=False, barWidth=0.2, colors=None, figsize=(13,6)):
        fig, ax = plt.subplots(figsize=figsize)

        averagedDataPerGroup = [] # [[0,0,0,0], [0,0,0,0], [0,0,0,0]]
        stderrPerGroup = []

        # iterate through subject groups
        for group in self.groups:
            individualAnswerData = []
            for s in group:
                subjectAnswers = s.learning_self_assessment_data

                # get question responses for each subject
                if len(individualAnswerData) == 0:
                    individualAnswerData = [[val] for val in subjectAnswers]
                else:
                    for q in range(len(individualAnswerData)):
                        individualAnswerData[q].append(subjectAnswers[q])
            
            # Take the average
            averagedData = [np.mean(q) for q in individualAnswerData]
            averagedDataPerGroup.append(averagedData)

            # Compute stdErr
            stderrData = [stats.sem(q) for q in individualAnswerData]
            stderrPerGroup.append(stderrData)

        print(averagedDataPerGroup)
            
        averagedDataPerGroup = np.array(averagedDataPerGroup).transpose()
        stderrPerGroup = np.array(stderrPerGroup).transpose()

        if not displayStderr:
            stderrPerGroup = None

        self.catBarPlot(averagedDataPerGroup, errData=stderrPerGroup, groupNames=self.groupNames, ax=ax, axisIndex=None, xLabel="Questions", yLabel="Response", title="Learning Self Assessment Data", colors=colors, barWidth=barWidth, figsize=figsize)
        plt.show()
    
