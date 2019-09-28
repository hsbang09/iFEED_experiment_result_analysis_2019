import csv
import json
import os
import numpy as np
import pandas as pd
import traceback

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

    def gradeAnswers(self, confidenceThreshold=None):
        self.feature_classification_score, self.feature_classification_graded_answers = self.grader.gradeAnswers("feature", "classification", self.feature_classification_answer, self.feature_classification_confidence, confidenceThreshold=confidenceThreshold)
        self.feature_comparison_score, self.feature_comparison_graded_answers = self.grader.gradeAnswers("feature", "comparison", self.feature_comparison_answer, self.feature_comparison_confidence, confidenceThreshold=confidenceThreshold)
        self.design_classification_score, self.design_classification_graded_answers = self.grader.gradeAnswers("design", "classification", self.design_classification_answer, self.design_classification_confidence, confidenceThreshold=confidenceThreshold)
        self.design_comparison_score, self.design_comparison_graded_answers = self.grader.gradeAnswers("design", "comparison", self.design_comparison_answer, self.design_comparison_confidence, confidenceThreshold=confidenceThreshold)

    def printScoreSummary(self):
        print("Subject: {0} - condition: {1}".format(self.participant_id, self.condition))
        print("Fcl: {0}, Fpwc: {1}, Dcl: {2}, Dpwc: {3}".format(self.feature_classification_score, self.feature_comparison_score, self.design_classification_score, self.design_comparison_score))

    def countFeatureParity(self, positive=True):
        return self.grader.countFeatureParity(self.feature_classification_graded_answers, self.feature_comparison_graded_answers, positive=positive)
