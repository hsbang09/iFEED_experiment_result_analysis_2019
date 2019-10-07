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


class Visualizer():

    def __init__(self, subjectGroups, subjectGroupNames=None):
        self.subjectGroups = subjectGroups
        self.subjectGroupNames = subjectGroupNames
        print(self.subjectGroups)
        
        
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

        
##################################### RENEE'S EDITS ###########################################

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
        
