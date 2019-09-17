import csv
import json
import os
import numpy as np
import pandas as pd
import traceback

FEATURE_QUESTION_ANSWER_OLD = [1,1,0,1,0,1,1,1,0,0, 1,1,0,0,1,0,0,0,1,0]
DESIGN_QUESTION_ANSWER_OLD = [0,0,1,1,0,0,1,0,1,1]

FEATURE_QUESTION_ANSWER = [1,0,0,0,1,1,1,0,0,1, 1,0,1,0,0,1,0,1,1,0]
DESIGN_QUESTION_ANSWER = [1,0,0,1,1,0,0,1,1,0]

COLNUM_PARTICIPANT_ID = 18 - 1
COLNUM_FEATURE_QUESTION = 19 - 1
COLNUM_DESIGN_QUESTION = 59 - 1
COLNUM_AGE = 126 - 1
COLNUM_GENDER = 127 - 1
COLNUM_EDUCATION = 128 - 1
COLNUM_MAJOR = 129 - 1
COLNUM_PRIOR_EXPERIENCE = 130 - 1
COLNUM_LEVEL_OF_EXPERIENCE = 131 - 1
COLNUM_YEARS_OF_EXPERIENCE = 132 - 1










class ResultAnalyzer():    

    def __init__(self, surveyDataFilePath, jsonFilesRootPath):
        self.subjects = []
        self.surveyDataFilePath = surveyDataFilePath
        self.jsonFilesRootPath = jsonFilesRootPath
        self.loadDataSet(surveyDataFilePath)

    def loadDataSet(self, surveyDataFilePath):
        if not os.path.isfile(surveyDataFilePath):
            raise OSError("Could not find the survey file: {0}".format(surveyDataFilePath))

        with open(surveyDataFilePath, 'r') as file:
            csvReader = csv.reader(file, delimiter=',')
            for i, row in enumerate(csvReader):
                if i < 3: # Skip header
                    pass
                else:
                    participant_id = row[COLNUM_PARTICIPANT_ID]

                    feature_question_answers = []
                    feature_question_confidence = []
                    for j in range(len(FEATURE_QUESTION_ANSWER) * 2):
                        if j % 2 == 0:
                            feature_question_answers.append(row[COLNUM_FEATURE_QUESTION + j])
                        else:
                            if row[COLNUM_FEATURE_QUESTION + j] == '':
                                continue
                            feature_question_confidence.append(int(row[COLNUM_FEATURE_QUESTION + j]))

                    design_question_answers = []
                    design_question_confidence = []
                    for j in range(len(DESIGN_QUESTION_ANSWER) * 2):
                        if j % 2 == 0:
                            design_question_answers.append(row[COLNUM_DESIGN_QUESTION + j])
                        else:
                            if row[COLNUM_DESIGN_QUESTION + j] == '':
                                continue
                            design_question_confidence.append(int(row[COLNUM_DESIGN_QUESTION + j]))

                    s = Subject(participant_id, old=old)
                    s.answer_feature_questions = feature_question_answers
                    s.confidence_feature_questions = feature_question_confidence
                    s.answer_design_questions = design_question_answers
                    s.confidence_design_questions = design_question_confidence

                    s.age = row[COLNUM_AGE]
                    s.gender = row[COLNUM_GENDER]
                    s.major = row[COLNUM_MAJOR]
                    s.prior_experience = row[COLNUM_PRIOR_EXPERIENCE]
                    self.subjects.append(s)











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









    # def grade_feature_questions(self):
    #     if self.answer_feature_questions is None:
    #         raise ValueError()
    #     if len(self.answer_feature_questions) != len(FEATURE_QUESTION_ANSWER):
    #         raise ValueError()

    #     self.graded_feature_questions = []
    #     for i in range(len(FEATURE_QUESTION_ANSWER)):
    #         answerCorrect = False

    #         if self.old:
    #             if self.answer_feature_questions[i] == 'YES' and FEATURE_QUESTION_ANSWER_OLD[i] == 1: # TRUE
    #                 answerCorrect = True
    #             elif self.answer_feature_questions[i] == 'NO' and FEATURE_QUESTION_ANSWER_OLD[i] == 0: # FALSE
    #                 answerCorrect = True
    #         else:
    #             if self.answer_feature_questions[i] == '1' and FEATURE_QUESTION_ANSWER[i] == 1: # TRUE
    #                 answerCorrect = True
    #             elif self.answer_feature_questions[i] == '2' and FEATURE_QUESTION_ANSWER[i] == 0: # FALSE
    #                 answerCorrect = True

    #         if answerCorrect:
    #             self.graded_feature_questions.append(1)
    #         else:
    #             self.graded_feature_questions.append(0)
    #     return sum(self.graded_feature_questions)

    # def grade_design_questions(self):
    #     if self.answer_design_questions is None:
    #         raise ValueError()
    #     if len(self.answer_design_questions) != len(DESIGN_QUESTION_ANSWER):
    #         raise ValueError()

    #     self.graded_design_questions = []
    #     for i in range(len(DESIGN_QUESTION_ANSWER)):
    #         answerCorrect = False

    #         if self.old:
    #             if self.answer_design_questions[i] == 'YES' and DESIGN_QUESTION_ANSWER_OLD[i] == 1: # TRUE
    #                 answerCorrect = True
    #             elif self.answer_design_questions[i] == 'NO' and DESIGN_QUESTION_ANSWER_OLD[i] == 0: # FALSE
    #                 answerCorrect = True
    #         else:
    #             if self.answer_design_questions[i] == '1' and DESIGN_QUESTION_ANSWER[i] == 1: # TRUE
    #                 answerCorrect = True
    #             elif self.answer_design_questions[i] == '2' and DESIGN_QUESTION_ANSWER[i] == 0: # FALSE
    #                 answerCorrect = True
            
    #         if answerCorrect:
    #             self.graded_design_questions.append(1)
    #         else:
    #             self.graded_design_questions.append(0)
    #     return sum(self.graded_design_questions)

    # def readJSONFiles(self):
    #     dirname = os.path.join(jsonFilePath, self.participant_id)

    #     if not os.path.isdir(dirname):
    #         raise ValueError()

    #     jsonFiles = [os.path.join(dirname, f) for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f)) and f.endswith(".json")]

    #     for filename in jsonFiles:
    #         with open(filename, newline='') as file:
    #             try:
    #                 data = json.loads(file.read())

    #                 if 'treatmentCondition' in data:
    #                     self.condition = data['treatmentCondition']
                    
    #                 if "learning" in os.path.basename(filename):
    #                     self.learning_task_data = data

    #                 elif "design_synthesis" in os.path.basename(filename):
    #                     self.design_synthesis_task_data = data

    #                 elif "conceptMap-0" in os.path.basename(filename):
    #                     self.pre_concept_map_data = data

    #                 elif "conceptMap-1" in os.path.basename(filename):
    #                     self.learning_concept_map_data = data

    #             except:
    #                 print("Exception while reading: {0}".format(filename))
    #                 traceback.print_exc()













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

