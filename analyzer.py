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
COLNUM_SELF_ASSESSMENT = 92 - 1
COLNUM_FEATURE_PREFERENCE = 96 - 1

# Column numbers: Demographic info
COLNUM_AGE = 105 - 1
COLNUM_GENDER = 106 - 1
COLNUM_EDUCATION = 107 - 1
COLNUM_MAJOR = 108 - 1
COLNUM_PRIOR_EXPERIENCE = 110 - 1
COLNUM_COMMENTS = 122

# Number of questions
NUM_FEATURE_CL_QUESTION = 9
NUM_FEATURE_PWC_QUESTION = 9
NUM_DESIGN_CL_QUESTION = 9
NUM_DESIGN_PWC_QUESTION = 9

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

                    feature_classification_answer = []
                    feature_classification_confidence = []
                    feature_comparison_answer = []
                    feature_comparison_confidence = []
                    design_classification_answer = []
                    design_classification_confidence = []
                    design_comparison_answer = []
                    design_comparison_confidence = []

                    for j in range(NUM_FEATURE_CL_QUESTION * 2):
                        val = row[COLNUM_FEATURE_CL_QUESTION + j]
                        if val == '':
                            raise ValueError()
                        val = int(val)

                        if j % 2 == 0:
                            feature_classification_answer.append(val)
                        else:
                            feature_classification_confidence.append(val)

                    for j in range(NUM_FEATURE_PWC_QUESTION * 2):
                        val = row[COLNUM_FEATURE_PWC_QUESTION + j]
                        if val == '':
                            raise ValueError()
                        val = int(val)

                        if j % 2 == 0:
                            feature_comparison_answer.append(val)
                        else:
                            feature_comparison_confidence.append(val)

                    for j in range(NUM_DESIGN_CL_QUESTION * 2):
                        val = row[COLNUM_DESIGN_CL_QUESTION + j]
                        if val == '':
                            raise ValueError()
                        val = int(val)

                        if j % 2 == 0:
                            design_classification_answer.append(val)
                        else:
                            design_classification_confidence.append(val)

                    for j in range(NUM_DESIGN_PWC_QUESTION * 2):
                        val = row[COLNUM_DESIGN_PWC_QUESTION + j]
                        if val == '':
                            raise ValueError()
                        val = int(val)

                        if j % 2 == 0:
                            design_comparison_answer.append(val)
                        else:
                            design_comparison_confidence.append(val)

                    s = Subject(self.jsonFilesRootPath, participant_id)
                    s.feature_classification_answer = feature_classification_answer
                    s.feature_classification_confidence = feature_classification_confidence
                    s.feature_comparison_answer = feature_comparison_answer
                    s.feature_comparison_confidence = feature_comparison_confidence
                    s.design_classification_answer = design_classification_answer
                    s.design_classification_confidence = design_classification_confidence
                    s.design_comparison_answer = design_comparison_answer
                    s.design_comparison_confidence = design_comparison_confidence








                    # # Column numbers: Other survey
                    # COLNUM_SELF_ASSESSMENT = 92 - 1
                    # COLNUM_FEATURE_PREFERENCE = 96 - 1



                    s.age = row[COLNUM_AGE]
                    s.gender = row[COLNUM_GENDER]
                    s.major = row[COLNUM_MAJOR]
                    s.prior_experience = row[COLNUM_PRIOR_EXPERIENCE]
                    self.subjects.append(s)



    def gradeAnswers(self, confidenceThreshold=None):
        for s in self.subjects:
            s.gradeAnswers(confidenceThreshold)






            




    def temp(self):
        filenames = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        self.data = []

        cnt = 0
        for filename in filenames:

            if filename.startswith("."):
                continue

            print(str(cnt) + ". " + filename.split("-")[0])
            cnt += 1

            s = Subject()
            s.readData(os.path.join(path, filename))
            self.data.append(s)

    def filterSubjects(self, subjects=None, pretest_score_threshold=None):
        out = []

        if subjects is None:
            subjects = self.data

        if pretest_score_threshold is not None:
            for sdata in subjects:
                score = sdata.getScore(problem_type="pretest")
                if score >= pretest_score_threshold:
                    out.append(sdata)

        return out

    def getScoreData(self, 
        subjects=None, 
        problem_type="design", 
        condition_number=None, 
        task_number=None, 
        exclude_first_task=False,
        skip_first_n_questions=0,
        conf_min=None, 
        conf_max=None, 
        time_min=None, 
        time_max=None):   

        if subjects is None:
            subjects = self.data

        out = []
        for i in range(len(subjects)):
            subject = subjects[i]

            if problem_type == "pretest":
                out.append(subject.getScore(problem_type=problem_type))

            else:
                if condition_number is None and task_number is None:
                    raise ValueError("Either the condition or the task number must be specified")


                if condition_number is not None and exclude_first_task:
                    if condition_number == subject.condition_order[0]: 
                        # If the first task matches the current condition, exclude this score
                        continue

                score = subject.getScore(condition_number=condition_number, 
                    task_number=task_number, 
                    problem_type=problem_type, 
                    conf_min=conf_min, 
                    conf_max=conf_max, 
                    time_min=time_min, 
                    time_max=time_max,
                    skip_first_n_questions=skip_first_n_questions)

                if score is not None:
                    out.append(score)

        return out

    def getConfidenceData(self, subjects=None, problem_type="design", condition_number=None, task_number=None, count_only_correct_answer=False, exclude_first_task=False):   
        
        if subjects is None:
            subjects = self.data


        out = []
        for i in range(len(subjects)):
            subject = subjects[i]

            if problem_type == "pretest":
                out.append(subject.getScore(problem_type=problem_type))
            else:
                if condition_number is None and task_number is None:
                    raise ValueError("Either the condition or the task number must be specified")

                if condition_number is not None and exclude_first_task:
                    if condition_number == subject.condition_order[0]: 
                        # If the first task matches the current condition, exclude this score
                        continue

                out.append(np.mean(subject.getConfidence(condition_number=condition_number, task_number=task_number, problem_type=problem_type, count_only_correct_answer=count_only_correct_answer)))

        return out


    def getTimeData(self, subjects=None, problem_type="design", condition_number=None, task_number=None, count_only_correct_answer=False, exclude_first_task=False):   
        
        if subjects is None:
            subjects = self.data


        out = []
        for i in range(len(subjects)):
            subject = subjects[i]

            if problem_type == "pretest":
                out.append(subject.getScore(problem_type=problem_type))

            else:
                if condition_number is None and task_number is None:
                    raise ValueError("Either the condition or the task number must be specified")

                if condition_number is not None and exclude_first_task:
                    if condition_number == subject.condition_order[0]: 
                        # If the first task matches the current condition, exclude this score
                        continue

                out.append(np.mean(subject.getTime(condition_number=condition_number, task_number=task_number, problem_type=problem_type, count_only_correct_answer=count_only_correct_answer)))

        return out

    def getConditionOrder(self, condition_number, subjects=None):

        if subjects is None:
            subjects = self.data

        out = []
        for i in range(len(subjects)):
            subject = subjects[i]

        return out

    def getSTEMMajors(self, subjects):
        out = []
        for subj in subjects:
            if subj.major == "13":   
                pass
            else:
                out.append(subj)  
        return out
    
    def getSubjectsWithPriorExperience(self, subjects):
        out = []
        for subj in subjects:
            if subj.prior_experience == "1": # Has-prior-experience  
                out.append(subj)  
        return out
    
    def filterByDemographics(self, STEM=False, NonSTEM=False, prior_experience=False, SYSEN5400 = False, NoSYSEN5400 = False):
        out = self.results
        if STEM:
            out = self.getSTEMMajors(out)
        if NonSTEM:
            stem = self.getSTEMMajors(out)
            out = []
            for subj in self.results:
                if subj not in stem:
                    out.append(subj)            
        if prior_experience:
            out = self.getSubjectsWithPriorExperience(out)
        if SYSEN5400:
            out = self.getSubjectsTakingSYSEN5400(out)
        if NoSYSEN5400:
            sysen5400 = self.getSubjectsTakingSYSEN5400(out)
            out = []
            for subj in self.results:
                if subj not in sysen5400:
                    out.append(subj)
        return out


    def importSurveyData(self, filename):
        
        content = None

        with open(filename, "r") as file:
            content = file.read() 

        rows = content.split("\n")
        for i, row in enumerate(rows):

            if i < 3:
                continue
            if len(row.split(",")) == 1:
                continue

            columns = row.split(",")

            key = columns[KEY_NUM_COLUMN]
            age = columns[AGE]
            gender = columns[GENDER]
            major = columns[MAJOR]

            if key == "szt3":
                continue

            elif key == "hl865":
                key = "7436259294"
            else:
                if key.startswith("\"") or key.endswith("\""):
                    key = key[1:-1]

                key = key.strip()

            if "-" in key:
                key = key.split("-")[0]

            if gender == "Male":
                gender = 0
            else:
                gender = 1

            if major in ["Computer Science / Information Science", "Industrial / Systems Engineering", "Electrical Engineering"]:
                major = 1
            else:
                major = 0

            subjectFound = False
            for s in self.data:
                if key == s.key:
                    subjectFound = True
                    s.setDemographicInfo(age,gender,major,False)

            if not subjectFound:
                raise ValueError("Subject not found: {0}".format(key))


    def saveCSV(self, filename=None):

        if filename is None:
            filename = "/Users/bang/workspace/iFEED_experiment_result_analysis_2018/data.csv"

        header = ["id","gender","major","pretestScore","condition1","condition2","condition3","order","score","time","confidence"]

        out = []

        out.append(",".join(header))

        # For each subject
        for s in self.data:
            summary = s.getDataSummary()

            for row in summary:
                row.insert(1,str(s.gender))
                row.insert(2,str(s.major))
                out.append(",".join(row))

        with open(filename, "w+") as file:
            file.write("\n".join(out))

                
    def printStatistics(self, subjects, condition_effect=True, order_effect=False):
        
        first_scores, second_scores = self.getScoreData(subjects, condition_effect, order_effect)
        
        first_mean = np.mean(first_scores)
        second_mean = np.mean(second_scores)
        first_std = np.std(first_scores)
        second_std = np.std(second_scores)
        
        if order_effect:    
            print("First Task Score Mean: {0}, Second Task Score Mean: {1}".format(first_mean, second_mean))
            print("First Task Score Stdev: {0}, Second Task Score Stdev: {1}".format(first_std, second_std))
        else:
            print("First Condition Score Mean: {0}, Second Condition Score Mean: {1}".format(first_mean, second_mean))
            print("First Condition Score Stdev: {0}, Second Condition Score Stdev: {1}".format(first_std, second_std))  
            
        return first_mean, second_mean, first_std, second_std











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

