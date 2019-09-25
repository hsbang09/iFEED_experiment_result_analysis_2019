import csv
import json
import os
import numpy as np
import pandas as pd
import traceback

from grader import Grader

class Subject():
    def __init__(self, jsonFilesRootPath, participant_id):
        self.jsonFilesRootPath = jsonFilesRootPath
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

        # Read JSON files
        self.readJSONFiles();

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

    def gradeAnswers(self, confidenceThreshold=None):
        self.feature_classification_score, self.feature_classification_graded_answers = self.grader.gradeAnswers("feature", "classification", self.feature_classification_answer, self.feature_classification_confidence, confidenceThreshold=confidenceThreshold)
        self.feature_comparison_score, self.feature_comparison_graded_answers = self.grader.gradeAnswers("feature", "comparison", self.feature_comparison_answer, self.feature_comparison_confidence, confidenceThreshold=confidenceThreshold)
        self.design_classification_score, self.design_classification_graded_answers = self.grader.gradeAnswers("design", "classification", self.design_classification_answer, self.design_classification_confidence, confidenceThreshold=confidenceThreshold)
        self.design_comparison_score, self.design_comparison_graded_answers = self.grader.gradeAnswers("design", "comparison", self.design_comparison_answer, self.design_comparison_confidence, confidenceThreshold=confidenceThreshold)

    def printScoreSummary(self):
        print("Subject: {0} - condition: {1}".format(self.participant_id, self.condition))
        print("Fcl: {0}, Fpwc: {1}, Dcl: {2}, Dpwc: {3}".format(self.feature_classification_score, self.feature_comparison_score, self.design_classification_score, self.design_comparison_score))

    def readJSONFiles(self):
        dirname = os.path.join(self.jsonFilesRootPath, self.participant_id)

        if not os.path.isdir(dirname):
            print("Failed to load the JSON file - directory not found: {0}".format(dirname))
            return
            # raise OSError("Directory not found: {0}".format(dirname))

        jsonFiles = [os.path.join(dirname, f) for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f)) and f.endswith(".json")]

        for filename in jsonFiles:
            with open(filename, newline='') as file:
                try:
                    data = json.loads(file.read())

                    if 'treatmentCondition' in data:
                        if self.condition is None:
                            # Condition 1: Manual - without generalization
                            # Condition 2: Automated - without generalization
                            # Condition 3: Interactive - without generalization
                            # Condition 4: Manual - with generalization
                            # Condition 5: Automated - with generalization
                            # Condition 6: Interactive - with generalization
                            self.condition = data['treatmentCondition']

                    if "learning" in os.path.basename(filename) and "conceptMap" not in os.path.basename(filename):
                        self.learning_task_data = data

                    elif "feature_synthesis" in os.path.basename(filename):
                        self.feature_synthesis_task_data = data

                    elif "design_synthesis" in os.path.basename(filename):
                        self.design_synthesis_task_data = data

                    elif "conceptMap-prior" in os.path.basename(filename):
                        self.cmap_prior_data = data

                    elif "conceptMap-learning" in os.path.basename(filename):
                        self.cmap_learning_data = data

                except:
                    print("Exception while reading: {0}".format(filename))
                    traceback.print_exc()

    def countFeatureParity(self, positive=True):
        return self.grader.countFeatureParity(self.feature_classification_graded_answers, self.feature_comparison_graded_answers, positive=positive)
