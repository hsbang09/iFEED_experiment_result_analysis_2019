import csv
import json
import os
import numpy as np
import pandas as pd
import traceback

from subject import Subject

# Column numbers: problems
COLNUM_PARTICIPANT_ID = 19 - 1
COLNUM_FEATURE_CL_QUESTION = 20 - 1
COLNUM_FEATURE_PWC_QUESTION = 38 - 1
COLNUM_DESIGN_CL_QUESTION = 56 - 1
COLNUM_DESIGN_PWC_QUESTION = 74 - 1

# Column numbers: Other survey
COLNUM_FEATURE_PREFERENCE = 92 - 1
COLNUM_SELF_ASSESSMENT = 101 - 1

# Column numbers: Demographic info
COLNUM_AGE = 105 - 1
COLNUM_GENDER = 106 - 1
COLNUM_EDUCATION = 107 - 1
COLNUM_MAJOR = 108 - 1
COLNUM_EMPLOYER_TYPE = 109 - 1
COLNUM_PRIOR_EXPERIENCE = 110 - 1
COLNUM_COMMENTS = 122

# Number of questions
NUM_FEATURE_CL_QUESTION = 9
NUM_FEATURE_PWC_QUESTION = 9
NUM_DESIGN_CL_QUESTION = 9
NUM_DESIGN_PWC_QUESTION = 9
NUM_FEATURE_PREFERENCE = 9
NUM_SELF_ASSESSMENT = 4
NUM_PRIOR_EXPERIENCE_QUESTION = 12


class ResultAnalyzer():    
    def __init__(self, surveyDataFilePath, jsonFilesRootPath, confidenceThreshold=None):
        self.subjects = []
        self.surveyDataFilePath = surveyDataFilePath
        self.jsonFilesRootPath = jsonFilesRootPath
        self.loadDataSet()

    def loadDataSet(self):
        if not os.path.isfile(self.surveyDataFilePath):
            raise OSError("Could not find the survey file: {0}".format(self.surveyDataFilePath))

        with open(self.surveyDataFilePath, 'r') as file:
            csvReader = csv.reader(file, delimiter=',')
            for i, row in enumerate(csvReader):
                if i < 3: # Skip header
                    pass
                else:
                    participant_id = row[COLNUM_PARTICIPANT_ID]

                    # Create new subject instance
                    s = Subject(self.jsonFilesRootPath, participant_id)
                    self.importProblemsetAnswers(row, s)
                    self.importFeaturePreferenceSurvey(row, s);
                    self.importSelfAssessmentOfLearning(row, s);
                    self.importDemographicSurvey(row, s);
                    self.importPriorExperienceSurvey(row, s);
                    self.subjects.append(s)


    def importProblemsetAnswers(self, inputRowData, subject):
        feature_classification_answer = []
        feature_classification_confidence = []
        feature_comparison_answer = []
        feature_comparison_confidence = []
        design_classification_answer = []
        design_classification_confidence = []
        design_comparison_answer = []
        design_comparison_confidence = []

        for j in range(NUM_FEATURE_CL_QUESTION * 2):
            val = inputRowData[COLNUM_FEATURE_CL_QUESTION + j]
            if val == '':
                raise ValueError()
            val = int(val)

            if j % 2 == 0:
                feature_classification_answer.append(val)
            else:
                feature_classification_confidence.append(val)

        for j in range(NUM_FEATURE_PWC_QUESTION * 2):
            val = inputRowData[COLNUM_FEATURE_PWC_QUESTION + j]
            if val == '':
                raise ValueError()
            val = int(val)

            if j % 2 == 0:
                feature_comparison_answer.append(val)
            else:
                feature_comparison_confidence.append(val)

        for j in range(NUM_DESIGN_CL_QUESTION * 2):
            val = inputRowData[COLNUM_DESIGN_CL_QUESTION + j]
            if val == '':
                raise ValueError()
            val = int(val)

            if j % 2 == 0:
                design_classification_answer.append(val)
            else:
                design_classification_confidence.append(val)

        for j in range(NUM_DESIGN_PWC_QUESTION * 2):
            val = inputRowData[COLNUM_DESIGN_PWC_QUESTION + j]
            if val == '':
                raise ValueError()
            val = int(val)

            if j % 2 == 0:
                design_comparison_answer.append(val)
            else:
                design_comparison_confidence.append(val)

        subject.feature_classification_answer = feature_classification_answer
        subject.feature_classification_confidence = feature_classification_confidence
        subject.feature_comparison_answer = feature_comparison_answer
        subject.feature_comparison_confidence = feature_comparison_confidence
        subject.design_classification_answer = design_classification_answer
        subject.design_classification_confidence = design_classification_confidence
        subject.design_comparison_answer = design_comparison_answer
        subject.design_comparison_confidence = design_comparison_confidence

    def importFeaturePreferenceSurvey(self, inputRowData, subject):
        # Feature preference survey
        temp = []
        for j in range(NUM_FEATURE_PREFERENCE):
            val = inputRowData[COLNUM_FEATURE_PREFERENCE + j]
            if val == '':
                raise ValueError()
            val = int(val)

            if j == 3:
                subject.feature_preference_data['generalization'] = temp
                temp = []
            elif j == 5:
                subject.feature_preference_data['generalizationPlusException'] = temp
                temp = []
            temp.append(val)
        subject.feature_preference_data['parity'] = temp

    def importSelfAssessmentOfLearning(self, inputRowData, subject):
        # Self assessment of learning
        for j in range(NUM_SELF_ASSESSMENT):
            val = inputRowData[COLNUM_SELF_ASSESSMENT + j]
            if val == '':
                colIndex = COLNUM_SELF_ASSESSMENT + j
                raise ValueError("Empty value: column {0} of the participant {1}".format(colIndex, participant_id))
            val = int(val)
            subject.learning_self_assessment_data.append(val)

    def importDemographicSurvey(self, inputRowData, subject):
        # Demographic survey
        subject.demographic_data['age'] = int(inputRowData[COLNUM_AGE])
        subject.demographic_data['gender'] = int(inputRowData[COLNUM_GENDER])
        subject.demographic_data['education'] = int(inputRowData[COLNUM_EDUCATION])
        subject.demographic_data['major'] = inputRowData[COLNUM_MAJOR]
        subject.demographic_data['employerType'] = inputRowData[COLNUM_EMPLOYER_TYPE]

    def importPriorExperienceSurvey(self, inputRowData, subject):
        # Prior experience survey
        subject.prior_experience_data['satelliteDesign'] = dict()
        subject.prior_experience_data['dataMining'] = dict()
        subject.prior_experience_data['tradespaceExploration'] = dict()

        for j in range(NUM_PRIOR_EXPERIENCE_QUESTION):
            val = inputRowData[COLNUM_PRIOR_EXPERIENCE + j]
            if val == '':
                val = 0
            else:
                val = int(val)

            if j == 0:
                subject.prior_experience_data['satelliteDesign']['exposure'] = val
            elif j == 1:
                subject.prior_experience_data['satelliteDesign']['experience'] = val
            elif j == 2:
                subject.prior_experience_data['satelliteDesign']['years'] = val
            elif j == 3:
                subject.prior_experience_data['satelliteDesign']['earthObservation'] = val
            elif j == 4:
                subject.prior_experience_data['satelliteDesign']['remoteSensing'] = val
            elif j == 5:
                subject.prior_experience_data['dataMining']['exposure'] = val
            elif j == 6:
                subject.prior_experience_data['dataMining']['experience'] = val
            elif j == 7:
                subject.prior_experience_data['dataMining']['years'] = val
            elif j == 8:
                subject.prior_experience_data['dataMining']['binaryClassification'] = val
            elif j == 9:
                subject.prior_experience_data['tradespaceExploration']['exposure'] = val
            elif j == 10:
                subject.prior_experience_data['tradespaceExploration']['experience'] = val
            elif j == 11:
                subject.prior_experience_data['tradespaceExploration']['years'] = val


    def gradeAnswers(self, confidenceThreshold=None):
        for s in self.subjects:
            s.gradeAnswers(confidenceThreshold)

    def filterSubjects(self, subjects=None, condition=None):
        out = []

        if subjects is None:
            subjects = self.subjects

        if condition is not None:
            if condition is list:
                for s in subjects:
                    if s.condition in condition:
                        out.append(s)
            else:
                for s in subjects:
                    if s.condition == condition:
                        out.append(s)
        return out







    # def getConfidenceData(self, subjects=None, problem_type="design", condition_number=None, task_number=None, count_only_correct_answer=False, exclude_first_task=False):   
    #     if subjects is None:
    #         subjects = self.data


    #     out = []
    #     for i in range(len(subjects)):
    #         subject = subjects[i]

    #         if problem_type == "pretest":
    #             out.append(subject.getScore(problem_type=problem_type))
    #         else:
    #             if condition_number is None and task_number is None:
    #                 raise ValueError("Either the condition or the task number must be specified")

    #             if condition_number is not None and exclude_first_task:
    #                 if condition_number == subject.condition_order[0]: 
    #                     # If the first task matches the current condition, exclude this score
    #                     continue

    #             out.append(np.mean(subject.getConfidence(condition_number=condition_number, task_number=task_number, problem_type=problem_type, count_only_correct_answer=count_only_correct_answer)))

    #     return out


    # def filterByDemographics(self, STEM=False, NonSTEM=False, prior_experience=False, SYSEN5400 = False, NoSYSEN5400 = False):
    #     out = self.results
    #     if STEM:
    #         out = self.getSTEMMajors(out)
    #     if NonSTEM:
    #         stem = self.getSTEMMajors(out)
    #         out = []
    #         for subj in self.results:
    #             if subj not in stem:
    #                 out.append(subj)            
    #     if prior_experience:
    #         out = self.getSubjectsWithPriorExperience(out)
    #     if SYSEN5400:
    #         out = self.getSubjectsTakingSYSEN5400(out)
    #     if NoSYSEN5400:
    #         sysen5400 = self.getSubjectsTakingSYSEN5400(out)
    #         out = []
    #         for subj in self.results:
    #             if subj not in sysen5400:
    #                 out.append(subj)
    #     return out

    # def saveCSV(self, filename=None):

    #     if filename is None:
    #         filename = "/Users/bang/workspace/iFEED_experiment_result_analysis_2018/data.csv"

    #     header = ["id","gender","major","pretestScore","condition1","condition2","condition3","order","score","time","confidence"]

    #     out = []

    #     out.append(",".join(header))

    #     # For each subject
    #     for s in self.data:
    #         summary = s.getDataSummary()

    #         for row in summary:
    #             row.insert(1,str(s.gender))
    #             row.insert(2,str(s.major))
    #             out.append(",".join(row))

    #     with open(filename, "w+") as file:
    #         file.write("\n".join(out))
  
    # def printStatistics(self, subjects, condition_effect=True, order_effect=False):
        
    #     first_scores, second_scores = self.getScoreData(subjects, condition_effect, order_effect)
        
    #     first_mean = np.mean(first_scores)
    #     second_mean = np.mean(second_scores)
    #     first_std = np.std(first_scores)
    #     second_std = np.std(second_scores)
        
    #     if order_effect:    
    #         print("First Task Score Mean: {0}, Second Task Score Mean: {1}".format(first_mean, second_mean))
    #         print("First Task Score Stdev: {0}, Second Task Score Stdev: {1}".format(first_std, second_std))
    #     else:
    #         print("First Condition Score Mean: {0}, Second Condition Score Mean: {1}".format(first_mean, second_mean))
    #         print("First Condition Score Stdev: {0}, Second Condition Score Stdev: {1}".format(first_std, second_std))  
            
    #     return first_mean, second_mean, first_std, second_std




def RepresentsInt(s):
    """Checks if a given string is a number or not

    Args:
        s (string): String input to check

    Returns:
        bool
    """
    try: 
        int(s)
        return True
    except ValueError:
        return False

            
if __name__=='__main__':
    pass    

