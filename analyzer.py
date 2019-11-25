import csv
import json
import os
import numpy as np
import pandas as pd
import traceback
import csv
import math
from subject import Subject
import cmapAnalysis as cma
import traceback

# Column numbers: problems
COLNUM_PARTICIPANT_ID = 20 - 1
COLNUM_FEATURE_CL_QUESTION = 21 - 1
COLNUM_FEATURE_PWC_QUESTION = 39 - 1
COLNUM_DESIGN_CL_QUESTION = 57 - 1
COLNUM_DESIGN_PWC_QUESTION = 75 - 1

# Column numbers: Other survey
COLNUM_FEATURE_PREFERENCE = 93 - 1
COLNUM_SELF_ASSESSMENT = 102 - 1

# Column numbers: Demographic info
COLNUM_AGE = 106 - 1
COLNUM_GENDER = 107 - 1
COLNUM_EDUCATION = 108 - 1
COLNUM_MAJOR = 109 - 1
COLNUM_EMPLOYER_TYPE = 110 - 1
COLNUM_PRIOR_EXPERIENCE = 111 - 1
COLNUM_COMMENTS = 123

# Number of questions
NUM_FEATURE_CL_QUESTION = 9
NUM_FEATURE_PWC_QUESTION = 9
NUM_DESIGN_CL_QUESTION = 9
NUM_DESIGN_PWC_QUESTION = 9
NUM_FEATURE_PREFERENCE = 9
NUM_SELF_ASSESSMENT = 4
NUM_PRIOR_EXPERIENCE_QUESTION = 12

GROUP_LABEL_MAP = {
    4: "manual",
    5: "automated",
    6: "interactive"
}

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
            val = 5 - int(val)
            subject.learning_self_assessment_data.append(val)
            
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
                        subject.computeDesignEntropy()

                    elif "conceptMap-prior" in os.path.basename(filename):
                        subject.cmap_prior_data = data

                    elif "conceptMap-learning_task_2" in os.path.basename(filename):
                        subject.cmap_learning_data_extended = data

                    elif "conceptMap-learning_task" in os.path.basename(filename):
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

    def getDataFrame(self, subjects=None, option="default", columns=None, 
                    invertSIB=False, 
                    excludeHV=True, 
                    adjustIGDUsingEntropy=False,
                    adjustIGDUsingEntireNumDesigns=True):

        if subjects is None:
            subjects = self.subjects

        colNames_scores = ["FID","FPWC",
                        "DID","DPWC",
                        "FScore","DScore",
                        "PScore","NScore",
                        "HScore","LScore",
                        "totalScore"]

        colNames_confidences = ["confFID","confFPWC","confDID","confDPWC"]

        colNames_learning = ["LT_numDesignViewed",
                            "LT_numFeatureViewed",
                            "LT_numFilterUsed",
                            "LT_numFeatureFound",
                            ]

        colNames_featureSynthesis = ["meanDist2UP",
                        "normalizedDist2UP",
                        "FS_numFeatureViewed",
                        "FS_numFilterUsed",
                        "FS_numFeatureTested"]


        colNames_designSynthesis = ["meanIGD","normalizedIGD","adjustedIGD",
                        "HV","adjustedHV",
                        "numDesigns","numDesignsToShortestDist",
                        "DS_numDesignViewed",
                        "DS_numDesignEvaluated",
                        "entropy",
                        ]

        colNames_cmapLearning = ["numNodes","numEdges","numHighLevelConcepts","numHighLevelEdges","normalizedCM"]

        colNames_selfAssessment = ["selfAssessment", "normalizedSA",
                                    "selfAssessmentQ1","normalizedSAQ1",
                                    "selfAssessmentExclude1","normalizedSAExclude1"]

        if option is not None:
            if option == "scores":
                tempColumns = colNames_scores

            elif option == "confidence":
                tempColumns = colNames_confidences

            elif option == "learningTask":
                tempColumns = colNames_learning

            elif option == "featureSynthesis":
                tempColumns = colNames_featureSynthesis

            elif option == "designSynthesis":
                tempColumns = colNames_designSynthesis

            elif option == "default":
                tempColumns = ["FID","FPWC","DID","DPWC",
                        "FScore","DScore",
                        "PScore","NScore",
                        "HScore","LScore",
                        "totalScore",
                        "meanDist2UP","normalizedDist2UP",
                        "meanIGD","normalizedIGD","adjustedIGD",
                        "HV","adjustedHV",
                        "numDesigns",
                        "selfAssessment",
                        "selfAssessmentExclude1",
                        "normalizedSA",
                        "entropy"]

            elif option == "all":
                tempColumns = colNames_scores + colNames_learning + colNames_confidences + colNames_featureSynthesis + colNames_designSynthesis + colNames_selfAssessment + colNames_cmapLearning
                tempColumns = list(set(tempColumns))

            else:
                raise ValueError("Option not recognized")

        else:
            tempColumns = []

        if columns is not None:
            columns = tempColumns + columns
        else:
            columns = tempColumns

        # Remove HV
        if excludeHV:
            if "HV" in columns:
                columns.remove("HV")
            if "adjustedHV" in columns:
                columns.remove("adjustedHV")

        dat = []
        for i, s in enumerate(subjects):
            rowData = []
            rowData.append(s.participant_id)
            rowData.append(GROUP_LABEL_MAP[s.condition])

            knowledgeType = "explicit"
            if s.condition == 4:
                knowledgeType = "implicit"
            rowData.append(knowledgeType)

            interactionType = "userInteraction"
            if s.condition == 5:
                interactionType = "noInteraction"
            rowData.append(interactionType)

            if i == 0:
                colNames = []
                colNames.append("id")
                colNames.append("condition")
                colNames.append("type1")
                colNames.append("type2")
                colNames += columns

            for col in columns:
                val = None

                ###### Problem set scores ######
                if col == "FID":
                    val = s.feature_classification_score

                elif col == "FPWC":
                    val = s.feature_comparison_score

                elif col == "DID":
                    val = s.design_classification_score

                elif col == "DPWC":
                    val = s.design_comparison_score

                elif col == "confFID":
                    val = np.mean(s.feature_classification_confidence) / 100
                    val = round(val, 3)

                elif col == "confFPWC":
                    val = np.mean(s.feature_comparison_confidence) / 100
                    val = round(val, 3)

                elif col == "confDID":
                    val = np.mean(s.design_classification_confidence) / 100
                    val = round(val, 3)

                elif col == "confDPWC":
                    val = np.mean(s.design_comparison_confidence) / 100
                    val = round(val, 3)

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

                elif col == "HScore":
                    val = s.gradeHighLevelFeatures()[0]

                elif col == "LScore":
                    val = s.gradeLowLevelFeatures()[0]

                ###### Learning task logged data ######
                elif col == "LT_numDesignViewed":
                    if s.learning_task_data:
                        val = s.learning_task_data['counter_design_viewed']

                elif col == "LT_numFeatureViewed":
                    if s.learning_task_data:
                        val = s.learning_task_data['counter_feature_viewed']

                elif col == "LT_numFilterUsed":
                    if s.learning_task_data:
                        val = s.learning_task_data['counter_filter_used']

                elif col == "LT_numFeatureFound":
                    if s.learning_task_data:
                        val = len(s.learning_task_data['features_found'])

                ###### Feature synthesis task data ######
                elif col == "meanDist2UP":
                    if s.feature_synthesis_task_data:
                        val = s.getDist2Utopia()
                        if invertSIB:
                            val = - val
                        val = round(val, 3)

                elif col == "normalizedDist2UP":
                    pass

                elif col == "FS_numFeatureViewed":
                    if s.feature_synthesis_task_data:
                        val = s.feature_synthesis_task_data['counter_feature_viewed']

                elif col == "FS_numFilterUsed":
                    if s.feature_synthesis_task_data:
                        val = s.feature_synthesis_task_data['counter_filter_used']

                elif col == "FS_numFeatureTested":
                    if s.feature_synthesis_task_data:
                        val = len(s.feature_synthesis_task_data['features_found'])

                ###### Design synthesis task data ######
                elif col == "meanIGD":
                    if s.design_IGD is None:
                        pass
                    else:
                        val = s.design_IGD
                        if invertSIB:
                            val = - val
                        val = round(val, 3)

                elif col == "normalizedIGD":
                    pass

                elif col == "numDesigns":
                    if s.design_synthesis_task_data:
                        val = len(s.design_synthesis_task_data['designs_evaluated'])

                elif col == "numDesignsToShortestDist":
                    val = s.design_num_designs_to_shortest_dist

                elif col == "DS_numDesignViewed":
                    if s.design_synthesis_task_data:
                        val = s.design_synthesis_task_data['counter_design_viewed']

                elif col == "DS_numDesignEvaluated":
                    if s.design_synthesis_task_data:
                        val = s.design_synthesis_task_data['counter_design_evaluated']

                elif col == "HV":
                    if s.design_HV is not None:
                        val = s.design_HV
                        val = round(val, 3)

                elif col == "entropy":
                    if s.design_entropy:
                        val = s.design_entropy
                        val = round(val, 3)

                ###### Concept map data ######
                elif col == "numNodes":
                    if s.cmap_learning_data_extended:
                        cmap = s.cmap_learning_data_extended
                    elif s.cmap_learning_data:
                        cmap = s.cmap_learning_data
                    else:
                        cmap = None
                    
                    if cmap is not None:
                        val = cma.getNumNodes(cmap)

                elif col == "numEdges":
                    if s.cmap_learning_data_extended:
                        cmap = s.cmap_learning_data_extended
                    elif s.cmap_learning_data:
                        cmap = s.cmap_learning_data
                    else:
                        cmap = None

                    if cmap is not None:
                        val = cma.getNumEdges(cmap)

                elif col == "numHighLevelEdges":
                    if s.cmap_learning_data_extended:
                        cmap = s.cmap_learning_data_extended
                    elif s.cmap_learning_data:
                        cmap = s.cmap_learning_data
                    else:
                        cmap = None

                    if cmap is not None:
                        val = cma.getNumEdges2HighLevelFeatures(cmap)

                elif col == "numHighLevelConcepts":
                    if s.cmap_learning_data_extended:
                        cmap = s.cmap_learning_data_extended
                    elif s.cmap_learning_data:
                        cmap = s.cmap_learning_data
                    else:
                        cmap = None

                    if cmap is not None:
                        val = cma.numHighLevelConceptUsed(cmap)

                elif col == "normalizedCM":
                    pass

                ###### Self learning assessment ######
                elif col == "selfAssessment":
                    if s.learning_self_assessment_data:
                        val = np.mean(s.learning_self_assessment_data)

                elif col == "selfAssessmentQ1":
                    if s.learning_self_assessment_data:
                        val = s.learning_self_assessment_data[0]

                elif col == "selfAssessmentExclude1":
                    if s.learning_self_assessment_data:
                        val = np.mean(s.learning_self_assessment_data[1:])
                        val = round(val, 3)

                elif col == "normalizedSA":
                    pass

                rowData.append(val)
            dat.append(rowData)

        out = pd.DataFrame(data=dat, index=None, columns=colNames)

        # Normalize the specified columns
        if "meanDist2UP" in colNames and "normalizedDist2UP" in colNames:
            out = self.normalizeValues(out, "meanDist2UP", "normalizedDist2UP", decimal=3, invert=True)

        if "meanIGD" in colNames and "normalizedIGD" in colNames:
            out = self.normalizeValues(out, "meanIGD", "normalizedIGD", decimal=3, invert=True)

        if "numDesigns" in colNames and "normalizedIGD" in colNames:
            out = self.adjustIGD(out, useEntropy=adjustIGDUsingEntropy, useEntireNumDesigns=adjustIGDUsingEntireNumDesigns)

        if "numDesigns" in colNames and "HV" in colNames:
            out = self.adjustHV(out)

        if "selfAssessment" in colNames and "normalizedSA" in colNames:
            out = self.normalizeValues(out, "selfAssessment", "normalizedSA", decimal=3)

        if "selfAssessmentQ1" in colNames and "normalizedSAQ1" in colNames:
            out = self.normalizeValues(out, "selfAssessmentQ1", "normalizedSAQ1", decimal=3)

        if "selfAssessmentExclude1" in colNames and "normalizedSAExclude1" in colNames:
            out = self.normalizeValues(out, "selfAssessmentExclude1", "normalizedSAExclude1", decimal=3)

        if "normalizedCM" in colNames and "numEdges" in colNames:
            out = self.normalizeValues(out, "numEdges", "normalizedCM", decimal=3)
        return out

    def getComments(self, subjects, type, targetKeyword, displayCondition=False, displayParticipantID=False, displayKeyword=False):
        out = []

        if type == "problem_solving_task":
            for s in subjects:

                tag = []
                if displayCondition:
                    tag.append(GROUP_LABEL_MAP[s.condition])
                if displayParticipantID:
                    tag.append(s.participant_id)

                if s.transcript_problem_solving is not None:
                    for key in s.transcript_problem_solving:
                        if targetKeyword in key:

                            message = ""

                            tagCopy = [s for s in tag]
                            if displayKeyword:
                                tagCopy.append(key)

                            if len(tagCopy) != 0:
                                tagString = " | ".join(tagCopy)
                                message = "[{0}] ".format(tagString)

                            message = message + s.transcript_problem_solving[key]
                            out.append(message)

        elif type == "survey":
            for s in subjects:

                tag = []
                if displayCondition:
                    tag.append(GROUP_LABEL_MAP[s.condition])
                if displayParticipantID:
                    tag.append(s.participant_id)

                if s.transcript_survey is not None:
                    for key in s.transcript_survey:
                        if targetKeyword in key:

                            message = ""
                            tagCopy = [s for s in tag]
                            if displayKeyword:
                                tagCopy.append(key)

                            if len(tagCopy) != 0:
                                tagString = " | ".join(tagCopy)
                                message = "[{0}] ".format(tagString)

                            message = message + s.transcript_survey[key]
                            out.append(message)
        return out

    """ Computes HV
    """             
    def computeHV(self, dataFilePath): 
        from moeaAnalysis import computeHV as _computeHV    

        scienceTotal = []
        costTotal = []

        # load in csv
        with open(dataFilePath) as csvfile:
            readCSV = csv.reader(csvfile, delimiter = ',')

            for row in readCSV:
                index = row[0]
                targetVal = row[1]
                science = row[3]
                cost = row[4]
                scienceTotal.append(float(science))
                costTotal.append(float(cost))

        # find min and max for cost for normalization
        costMax = max(costTotal)
        costMin = min(costTotal)
        sciMax = max(scienceTotal)
        sciMin = min(scienceTotal)
        costDiff = costMax - costMin
        sciDiff = sciMax - sciMin

        for s in self.subjects:
            # create variable with the subject's design info
            designs = s.design_synthesis_task_data['designs_evaluated']
            numDesigns = len(designs)
            
            solutions = []
            for d in designs:
                nSci = 1 - (d['outputs'][0] - sciMin) / sciDiff
                nCost = (d['outputs'][1] - costMin) / costDiff
                solutions.append([nSci, nCost])

            hv = _computeHV(solutions, num_objectives=2, ref_point=None)
            s.design_HV = hv

    """ Computes IGD
    """             
    def computeIGD(self, dataFilePath, useShortestDistance=False):    
        classLabel = []
        allSci = []
        allCost = []

        # load in csv
        with open(dataFilePath) as csvfile:
            readCSV = csv.reader(csvfile, delimiter = ',')
            for row in readCSV:
                index = row[0]
                targetVal = row[1]
                science = row[3]
                cost = row[4]
                classLabel.append(int(targetVal))
                allSci.append(float(science))
                allCost.append(float(cost))

        # initialize empty arrays
        tSci = []
        tCost = []
        numTargets = 0

        # find min and max for cost for normalization
        costMax = max(allCost)
        costMin = min(allCost)
        sciMax = max(allSci)
        sciMin = min(allSci)
        costDiff = costMax - costMin
        sciDiff = sciMax - sciMin

        # iterate through the column that contains a 0 or 1 describing if 
        # design is a target. if Yes (targetbool = 1), append science and cost
        # to array
        for i, label in enumerate(classLabel):
            if label == 1:
                tSci.append( (allSci[i] - sciMin) / sciDiff )
                tCost.append( (allCost[i] - costMin) / costDiff )
        numTargets = len(tSci)

        for s in self.subjects:
            # create variable with the subject's design info
            if not s.design_synthesis_task_data:
                s.design_IGD = None
                s.design_num_designs_to_shortest_dist = None
                continue

            subDesigns = s.design_synthesis_task_data['designs_evaluated']
            numDesigns = len(subDesigns)
            minDistList = []

            # iterate through each subject's solutions, get the min distance to the target region
            for sDesign in subDesigns:
                sSci = (sDesign['outputs'][0] - sciMin) / sciDiff
                sCost = (sDesign['outputs'][1] - costMin) / costDiff       
                 
                # iterate through target solutions get the min distance
                minDist = 10
                for i in range(numTargets):
                    dist = math.sqrt((sCost - tCost[i])**2 + (sSci - tSci[i])**2)
                    if dist < minDist:
                        minDist = dist
                
                # add min of the distances to an array    
                minDistList.append(minDist)

            s.design_synthesis_task_data["minDistList"] = minDistList

            if useShortestDistance:
                minDist = min(minDistList)
                s.design_IGD = minDist
                s.design_num_designs_to_shortest_dist = -1

                for i in range(len(minDistList)):
                    if minDistList[i] == minDist:
                        s.design_num_designs_to_shortest_dist = i+1
                        break
            else:
                # sum and average  
                s.design_IGD = np.mean(minDistList)

    def adjustIGD(self, dataframe, useEntropy=False, useEntireNumDesigns=True, decimal=3):
        normalizedIGD = dataframe["normalizedIGD"].values
        numDesigns = dataframe["numDesigns"].values

        if useEntropy:
            entropies = dataframe["entropy"].values
        else:
            if not useEntireNumDesigns:
                numDesignsToShortestDist = dataframe["numDesignsToShortestDist"].values

        adjustedIGD = []
        for i in range(len(normalizedIGD)):
            val = None
            if useEntropy:
                val = normalizedIGD[i] / entropies[i]
            elif useEntireNumDesigns:
                val = normalizedIGD[i] / numDesigns[i]
            else:
                val = normalizedIGD[i] / numDesignsToShortestDist[i]
            adjustedIGD.append(val)

        minVal = min(adjustedIGD) 
        maxVal = max(adjustedIGD)
        normalized = [ round((x - minVal) / (maxVal - minVal), decimal) for x in adjustedIGD]
        dataframe["adjustedIGD"] = normalized
        return dataframe

    def adjustHV(self, dataframe, decimal=3):
        HVs = dataframe["HV"].values
        numDesigns = dataframe["numDesigns"].values

        adjustedHVs = []
        for i in range(len(HVs)):
            val = HVs[i] / numDesigns[i]
            adjustedHVs.append(val)

        minVal = min(adjustedHVs) 
        maxVal = max(adjustedHVs)
        normalized = [ round((x - minVal) / (maxVal - minVal), decimal) for x in adjustedHVs]
        dataframe["adjustedHV"] = normalized
        return dataframe

    def normalizeValues(self, dataframe, originalName, newName, decimal=3, invert=False):
        vals = dataframe[originalName].values

        if invert:
            vals = [-x for x in vals]

        minVal = min(vals) 
        maxVal = max(vals)
        normalized = [ round((x - minVal) / (maxVal - minVal), decimal) for x in vals]
        dataframe[newName] = normalized
        return dataframe

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



    # def plotECDF(scores1,scores2):
        
    #     import statsmodels.api as sm # recommended import according to the docs

    #     sample = scores1
    #     ecdf = sm.distributions.ECDF(scores1)
    #     x = np.linspace(min(sample), max(sample))
    #     y = ecdf(x)
    #     plt.step(x, y)

    #     sample2 = scores2
    #     ecdf = sm.distributions.ECDF(sample2)
    #     x = np.linspace(min(sample2), max(sample2))
    #     y = ecdf(x)
    #     plt.step(x, y)

    #     plt.show()

    # def writeToFile(data, header ,filePath = "/Users/bang/workspace/iFEED-experiment-201711-result/data/data.csv"):
    #     with open(filePath, 'w') as f:
    #         f.write(header + "\n")
    #         for row in data:
    #             f.write(",".join(row) + "\n")
        





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

