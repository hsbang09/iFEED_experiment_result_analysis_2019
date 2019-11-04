import csv
import json
import os
import math
import numpy as np
import pandas as pd
import traceback
import math

from grader import Grader

class Subject():
    def __init__(self, participant_id):
        self.participant_id = participant_id
        self.condition = None

        # Data logged from iFEED
        self.learning_task_data = dict()
        self.design_synthesis_task_data = dict()
        self.feature_synthesis_task_data = dict()
        
        # Concept map data
        self.cmap_prior_data = dict()
        self.cmap_learning_data = dict()
        self.cmap_learning_data_extended = dict()

        # Problem answers
        self.feature_classification_answer = []
        self.feature_classification_confidence = []
        self.feature_comparison_answer = []
        self.feature_comparison_confidence = []
        self.design_classification_answer = []
        self.design_classification_confidence = []
        self.design_comparison_answer = []
        self.design_comparison_confidence = []

        # Feature preference questions
        self.feature_preference_data = dict()

        # Self-assessment of learning
        self.learning_self_assessment_data = []

        # Demographic info
        self.demographic_data = dict()
        self.prior_experience_data = dict()

        # Graded score and answers
        self.grader = Grader()
        self.feature_classification_score = None
        self.feature_classification_graded_answers = []
        self.feature_comparison_score = None
        self.feature_comparison_graded_answers = []
        self.design_classification_score = None
        self.design_classification_graded_answers = []
        self.design_comparison_score = None
        self.design_comparison_graded_answers = []

        # Transcript data
        self.transcript_problem_solving = None
        self.transcript_survey = None
        
        # IDG and distance to utopia
        self.feature_synthesis_dist2UP = dict()
        self.design_IGD = dict()
        self.design_HV = None

    def gradeAnswers(self, confidenceThreshold=None):
        self.feature_classification_score, self.feature_classification_graded_answers = self.grader.gradeAnswers("feature", "classification", self.feature_classification_answer, self.feature_classification_confidence, confidenceThreshold=confidenceThreshold)
        self.feature_comparison_score, self.feature_comparison_graded_answers = self.grader.gradeAnswers("feature", "comparison", self.feature_comparison_answer, self.feature_comparison_confidence, confidenceThreshold=confidenceThreshold)
        self.design_classification_score, self.design_classification_graded_answers = self.grader.gradeAnswers("design", "classification", self.design_classification_answer, self.design_classification_confidence, confidenceThreshold=confidenceThreshold)
        self.design_comparison_score, self.design_comparison_graded_answers = self.grader.gradeAnswers("design", "comparison", self.design_comparison_answer, self.design_comparison_confidence, confidenceThreshold=confidenceThreshold)

    def getMeanConfidence(self, problemTopic=None, problemType=None, countOnlyCorrectAnswers=False, countOnlyWrongAnswers=False):
        if self.feature_classification_score is None or self.feature_comparison_score is None or self.design_classification_score is None or self.design_comparison_score is None:
            raise ValueError()
        
        gradedAnswers = []
        confidences = []

        if problemTopic is None and problemType is None:
            gradedAnswers = self.feature_classification_graded_answers + self.feature_comparison_graded_answers + self.design_classification_graded_answers + self.design_comparison_graded_answers
            confidences = self.feature_classification_confidence + self.feature_comparison_confidence + self.design_classification_confidence + self.design_comparison_confidence

        targetGrade = None
        if countOnlyCorrectAnswers:
            targetGrade = 1
        elif countOnlyWrongAnswers:
            targetGrade = 0

        if targetGrade is not None:
            tempConfidences = []
            for i, c in enumerate(gradedAnswers):
                if gradedAnswers[i] == targetGrade:
                    tempConfidences.append(confidences[i])
            confidences = tempConfidences

        return np.mean(confidences)                

    def printloggedDataSummary(self, task=None, loggedData=None):
        if task is None and loggedData is None:
            raise ValueError()

        if task is not None:
            if task == "learning_task":
                data = self.learning_task_data
            elif task == "feature_synthesis_task":
                data = self.feature_synthesis_task_data
            elif task == "design_synthesis_task":
                data = self.design_synthesis_task_data

        elif loggedData is not None:
            data = loggedData
            
        out = ["Subject: {0} - condition: {1}".format(self.participant_id, self.condition)]
        for key in data.keys():
            if key in ["participantID", "treatmentCondition", "stage", "duration", "paramsInfo"]:
                continue

            val = data[key]
            if key == "designs_evaluated":
                val = str(len(data[key]))

            elif key == "features_found":
                val = str(len(data[key]))

            out.append("{0}: {1}".format(key, val))
        print("\n".join(out))

    def getAggregateScore(self, combineFandD=True):
        FScore = (self.feature_classification_score + self.feature_comparison_score) / 2
        DScore = (self.design_classification_score + self.design_comparison_score ) / 2
        if combineFandD:
            total = (FScore + DScore) / 2
            return round(total, 2)
        else:
            FScore = round(FScore, 2)
            DScore = round(DScore, 2)
            return FScore, DScore

    def printAggregateScore(self, combineFandD=True):
        print("Subject: {0} - condition: {1}".format(self.participant_id, self.condition))
        if combineFandD:
            total = self.getAggregateScore(combineFandD=combineFandD)
            print("Total score: {0}".format(total))
        else:
            FScore, DScore = self.getAggregateScore(combineFandD=combineFandD)
            print("Feature: {0}, Design: {1}".format(FScore, DScore))

    def printScoreSummary(self):
        print("Subject: {0} - condition: {1}".format(self.participant_id, self.condition))
        print("Fcl: {0}, Fpwc: {1}, Dcl: {2}, Dpwc: {3}".format(self.feature_classification_score, self.feature_comparison_score, self.design_classification_score, self.design_comparison_score))

    def gradePositiveFeatures(self):
        return self.grader.gradePositiveOrNegativeFeatures(self.feature_classification_graded_answers, self.feature_comparison_graded_answers, positive=True)

    def gradeNegativeFeatures(self):
        return self.grader.gradePositiveOrNegativeFeatures(self.feature_classification_graded_answers, self.feature_comparison_graded_answers, positive=False)

    def gradeHighLevelFeatures(self):
        return self.grader.gradeHighVsLowLevelFeatures(self.feature_classification_graded_answers, self.feature_comparison_graded_answers, highLevel=True)

    def gradeLowLevelFeatures(self):
        return self.grader.gradeHighVsLowLevelFeatures(self.feature_classification_graded_answers, self.feature_comparison_graded_answers, highLevel=False)

    def getDist2Utopia(self):
        if len(self.feature_synthesis_task_data) != 0 and 'features_found' in self.feature_synthesis_task_data:
            features = self.feature_synthesis_task_data['features_found']
            self.feature_synthesis_dist2UP = 1
            for count, feature in enumerate(features):
                x = feature['metrics'][2]
                y = feature['metrics'][3]
                dist = math.sqrt((1.0 - x)**2 + (1.0 - y)**2)
                if dist <  self.feature_synthesis_dist2UP:
                    self.feature_synthesis_dist2UP = dist

        return self.feature_synthesis_dist2UP

    def computeDesignEntropy(self):
        def rearrangeDesignInputs(inputs):
            inputAppearance = []
            
            for designIndex, designInputString in enumerate(inputs):
                if len(inputAppearance) == 0:
                    inputAppearance = [[] for k in range(len(designInputString))]
                
                for inputIndex, val in enumerate(designInputString):
                    if val == "1":
                        inputAppearance[inputIndex].append(designIndex)
            return inputAppearance

        def getEntropy(inputAppearances, base=10):
            N = len(inputAppearances)
            
            sig = 0
            for i, appearances in enumerate(inputAppearances):
                if len(appearances) == 0:
                    continue
                else:
                    p = len(appearances) / N
                    sig += p * math.log(p,base) 
            H = - 1 / math.log(N, base) * sig
            return H

        inputs = []
        designs = self.design_synthesis_task_data['designs_evaluated']
        for d in designs:
            inputs.append(d['inputs'])
        inputAppearances = rearrangeDesignInputs(inputs)
        entropy = getEntropy(inputAppearances)
        self.design_entropy = entropy
