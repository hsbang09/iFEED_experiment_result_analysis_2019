import csv
import json
import os
import numpy as np
import pandas as pd
import traceback
import math
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
    def __init__(self, surveyDataFilePath, loggedDataRootPath, confidenceThreshold=None):
        self.subjects = []
        self.surveyDataFilePath = surveyDataFilePath
        self.loggedDataRootPath = loggedDataRootPath
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
                    s = Subject(participant_id)
                    self.importProblemsetAnswers(row, s)
                    self.importFeaturePreferenceSurvey(row, s)
                    self.importSelfAssessmentOfLearning(row, s)
                    self.importDemographicSurvey(row, s)
                    self.importPriorExperienceSurvey(row, s)
                    self.importJSONFiles(s)
                    self.importTranscriptFiles(s)
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
            elif j == 6:
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
            
            
    def dist2Utopia(self, subject):
        sub = subject.feature_synthesis_task_data['features_found']
        subject.feature_synthesis_dist2UP = 1
        print(1)
        for count, feature in enumerate(sub):
            x = subject.feature_synthesis_task_data['features_found'][count]['metrics'][2]
            y = subject.feature_synthesis_task_data['features_found'][count]['metrics'][3]
            distNew = math.sqrt((1.0 - x)**2 + (1.0 - y)**2)
            if distNew <  subject.feature_synthesis_dist2UP:
                subject.feature_synthesis_dist2UP = distNew
                

    def importDemographicSurvey(self, inputRowData, subject):
        # Demographic survey
        subject.demographic_data['age'] = int(inputRowData[COLNUM_AGE])
        subject.demographic_data['gender'] = int(inputRowData[COLNUM_GENDER])
        subject.demographic_data['education'] = int(inputRowData[COLNUM_EDUCATION])
                      
        def majorIndex2String(major): 
            switcher = {  
                1: "Aerospace Engineering", 
                2: "Biological / Agricultural / Biomedial Engineering", 
                3: "Chemical Engineering",
                4: "Civil / Environmental Engineering",
                5: "Computer Science / Information Science",
                6: "Electrical Engineering",
                7: "Industrial / Systems Engineering",
                8: "Mechanical Engineering",
                9: "Mathematics / Statistics",
                10: "Physics",
                11: "Chemistry",
                12: "Biological Science",
                13: "Other",
            } 
            return switcher.get(major, "nothing")

        subject.demographic_data['major'] = inputRowData[COLNUM_MAJOR]
        majorIndexString = subject.demographic_data['major']
        majorStringList = [majorIndex2String(int(i)) for i in majorIndexString.split(',')]
        subject.demographic_data['major'] = ', '.join(majorStringList)
        
        def employerTypeIndex2String(argument): 
            switcher = {  
                1: "For profit", 
                2: "Non-profit (non-profit research organization, government contractor, etc.)", 
                3: "Government",
                4: "Academic institution",
                5: "Other",
            } 
            return switcher.get(argument, "nothing") 
        
        subject.demographic_data['employerType'] = inputRowData[COLNUM_EMPLOYER_TYPE]
        employerIndexString = subject.demographic_data['employerType']
        employerStringList = [employerTypeIndex2String(int(i)) for i in employerIndexString.split(',')]
        subject.demographic_data['employerType'] = ', '.join(employerStringList)

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

    def importJSONFiles(self, subject):
        dirname = os.path.join(self.loggedDataRootPath, subject.participant_id)

        if not os.path.isdir(dirname):
            print("Failed to load JSON file - directory not found: {0}".format(dirname))
            return

        jsonFiles = [os.path.join(dirname, f) for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f)) and f.endswith(".json")]

        for filename in jsonFiles:
            with open(filename, newline='') as file:
                try:
                    data = json.loads(file.read())

                    if 'treatmentCondition' in data:
                        if subject.condition is None:
                            # Condition 1: Manual - without generalization
                            # Condition 2: Automated - without generalization
                            # Condition 3: Interactive - without generalization
                            # Condition 4: Manual - with generalization
                            # Condition 5: Automated - with generalization
                            # Condition 6: Interactive - with generalization
                            subject.condition = data['treatmentCondition']

                    if "learning" in os.path.basename(filename) and "conceptMap" not in os.path.basename(filename):
                        subject.learning_task_data = data

                    elif "feature_synthesis" in os.path.basename(filename):
                        subject.feature_synthesis_task_data = data

                    elif "design_synthesis" in os.path.basename(filename):
                        subject.design_synthesis_task_data = data

                    elif "conceptMap-prior" in os.path.basename(filename):
                        subject.cmap_prior_data = data

                    elif "conceptMap-learning" in os.path.basename(filename):
                        subject.cmap_learning_data = data

                except:
                    print("Exception while reading: {0}".format(filename))
                    traceback.print_exc()

    def importTranscriptFiles(self, subject):
        dirname = os.path.join(self.loggedDataRootPath, subject.participant_id)

        if not os.path.isdir(dirname):
            print("Failed to load transcript file - directory not found: {0}".format(dirname))
            return

        transcriptFiles = [os.path.join(dirname, f) for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f)) and f.endswith(".txt") and "transcript" in f]

        for filename in transcriptFiles:
            with open(filename, newline='') as file:
                try:
                    content = file.read()
                    if "problem_solving_task" in filename:
                        subject.transcript_problem_solving = self.parseTranscript("problem_solving_task", content)

                    elif "survey" in filename:
                        subject.transcript_survey = self.parseTranscript("survey", content)

                except:
                    print("Failed to load transcript file: {0}".format(filename))
                    traceback.print_exc()
                    
    def parseTranscript(self, type, content):
        out = dict()
        contentLines = content.split("\n")

        if type == "problem_solving_task":
            problemTopic = ["F", "D"]
            problemType = ["cl", "pwc"]
            problemNum = 9

            for pTopic in problemTopic:
                for pType in problemType:
                    for i in range(problemNum):
                        problemKey = "_".join([pTopic, pType, str(i+1)])

                        recordContent = False
                        problemSpecificContent = []
                        for line in contentLines:
                            if problemKey in line:
                                recordContent = True
                                continue

                            if recordContent:
                                if "[F_" in line or "[D_" in line:
                                    recordContent = False
                                    break
                                else:
                                    if not line.strip():
                                        # Empty space
                                        pass
                                    else:
                                        problemSpecificContent.append(line)

                        out[problemKey] = "\n".join(problemSpecificContent)

        elif type == "survey":
            surveyQuestionNum = 9
            for i in range(surveyQuestionNum):

                questionKey = "[{0}]".format(str(i+1))
                nextQuestionKey = "[{0}]".format(str(i+2))
                recordContent = False
                questionSpecificContent = []

                for line in contentLines:
                    if questionKey in line:
                        recordContent = True
                        continue

                    if recordContent:
                        if nextQuestionKey in line:
                            recordContent = False
                            break
                        else:
                            if not line.strip():
                                # Empty space
                                pass
                            else:
                                questionSpecificContent.append(line)

                questionType = None
                if i < 3:
                    questionType = "gen"
                elif i < 6:
                    questionType = "gpe"
                elif i < 9:
                    questionType = "par"
                out["{0}_{1}".format(str(i+1), questionType)] = "\n".join(questionSpecificContent)

        return out

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

    def getDataFrame(self, subjects=None, columns=None):
        if subjects is None:
            subjects = self.subjects

        if columns is None:
            columns = ["fcl","fpwc","dcl","dpwc","FScore","DScore","PScore","NScore","totalScore"]

        dat = []
        for i, s in enumerate(subjects):
            rowData = []
            rowData.append(s.participant_id)
            rowData.append(s.condition)

            if i == 0:
                colNames = []
                colNames.append("id")
                colNames.append("condition")
                colNames += columns

            for col in columns:
                val = None
                if col == "fcl":
                    val = s.feature_classification_score

                elif col == "fpwc":
                    val = s.feature_comparison_score

                elif col == "dcl":
                    val = s.design_classification_score

                elif col == "dpwc":
                    val = s.design_comparison_score

                elif col == "FScore":
                    val = s.getAggregateScore(combineFandD=False)[0]

                elif col == "DScore":
                    val = s.getAggregateScore(combineFandD=False)[1]

                elif col == "totalScore":
                    val = s.getAggregateScore(combineFandD=True)

                elif col == "PScore":
                    val = s.gradePositiveFeatures()[0]

                elif col == "NScore":
                    val = s.gradeNegativeFeatures()[0]

                elif col == "counter_design_viewed":
                    val = s.learning_task_data['counter_design_viewed']

                elif col == "counter_feature_viewed":
                    val = s.learning_task_data['counter_feature_viewed']

                elif col == "counter_filter_used":
                    val = s.learning_task_data['counter_filter_used']
                rowData.append(val)
            dat.append(rowData)

        out = pd.DataFrame(data=dat, index=None, columns=colNames)
        return out




    # def printAggregateScore(self, subjects=None, combineFandD=True):
    #     if subjects is None:
    #         subjects = self.subjects

    #     for s in subjects:

    #     print("Subject: {0} - condition: {1}".format(self.participant_id, self.condition))
    #     FScore = (self.feature_classification_score + self.feature_comparison_score) / 2
    #     DScore = (self.design_classification_score + self.design_comparison_score ) / 2
    #     total = (FScore + DScore) / 2
    #     if combineFandD:
    #         print("[Condition {0}] Total score: {1}".format(total))
    #     else:
    #         print("Feature: {0}, Design: {1}".format(FScore, DScore))

    # def printScoreSummary(self, subjects):
    #     print("Subject: {0} - condition: {1}".format(self.participant_id, self.condition))
    #     print("Fcl: {0}, Fpwc: {1}, Dcl: {2}, Dpwc: {3}".format(self.feature_classification_score, self.feature_comparison_score, self.design_classification_score, self.design_comparison_score))

    # def countFeatureParity(self, positive=True):
    #     return self.grader.countFeatureParity(self.feature_classification_graded_answers, self.feature_comparison_graded_answers, positive=positive)


    def getComments(self, subjects, type, targetKeyword, displayParticipantID=False, displayKeyword=False):
        out = []
        if type == "problem_solving_task":
            for s in subjects:
                if s.transcript_problem_solving is not None:
                    for key in s.transcript_problem_solving:
                        if targetKeyword in key:

                            message = ""
                            if displayParticipantID or displayKeyword:
                                identifier = []
                                if displayParticipantID:
                                    identifier.append(s.participant_id)
                                if displayKeyword:
                                    identifier.append(key)
                                identifier = ":".join(identifier)
                                message = "[{0}] ".format(identifier)

                            message = message + s.transcript_problem_solving[key]
                            out.append(message)

        elif type == "survey":
            for s in subjects:
                if s.transcript_survey is not None:
                    for key in s.transcript_survey:
                        if targetKeyword in key:

                            message = ""
                            if displayParticipantID or displayKeyword:
                                identifier = []
                                if displayParticipantID:
                                    identifier.append(s.participant_id)
                                if displayKeyword:
                                    identifier.append(key)
                                identifier = ":".join(identifier)
                                message = "[{0}] ".format(identifier)

                            message = message + s.transcript_survey[key]
                            out.append(message)
        return out



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

