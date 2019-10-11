
FEATURE_CL_QUESTION_ANSWER = [0, 1, 1, 1, 0, 0, 1, 0, 1]
FEATURE_PWC_QUESTION_ANSWER = [1, 0, 1, 0, 1, 1, 1, 0, 0]
DESIGN_CL_QUESTION_ANSWER = [1, 0, 0, 1, 1, 0, 1, 0, 1]
DESIGN_PWC_QUESTION_ANSWER = [1, 0, 0, 1, 1, 0, 0, 0, 1]

FEATURE_CL_PARITY = [1, 0, 0, 1, 1, 0, 0, 0, 1] # positive - 1, negative - 0
FEATURE_PWC_PARITY = [0, 1, 0, 1, 1, 0, 1, 1, 0] # positive - 1, negative - 0

FEATURE_CL_HIGH_LEVEL = [0, 1, 1, 0, 1, 0, 0, 0, 0] 
FEATURE_PWC_HIGH_LEVEL = [0, 0, 1, 1, 0, 1, 0, 1, 0] 

class Grader():
    def __init__(self):
        pass

    def gradeAnswers(self, problemTopic, problemType, answers, confidence=None, parity=False, confidenceThreshold=None):
        """Grades the answers and outputs the total score in %, 
        and the list containing 1 or 0's indicating whether each answer was right or wrong.

        Args:
            problemTopic (str): "feature" or "design"
            problemType (str): "classification" or "comparison"

        Returns:
            score: Score in float
            gradedAnswers: List of integers (1 or 0)
        """
        correctAnswers = None
        if problemTopic == "feature" and problemType == "classification":
            correctAnswers = FEATURE_CL_QUESTION_ANSWER
        elif problemTopic == "feature" and problemType == "comparison":
            correctAnswers = FEATURE_PWC_QUESTION_ANSWER
        elif problemTopic == "design" and problemType == "classification":
            correctAnswers = DESIGN_CL_QUESTION_ANSWER
        elif problemTopic == "design" and problemType == "comparison":
            correctAnswers = DESIGN_PWC_QUESTION_ANSWER
        else:
            raise ValueError()

        if len(correctAnswers) != len(answers):
            raise ValueError()

        graded = []
        if problemType == "classification":
            for i in range(len(answers)):

                if confidenceThreshold is not None:
                    if confidence[i] < confidenceThreshold: # Failed to pass confidence level test
                        graded.append(0) # Mark the answer wrong without checking the answer
                        continue

                if correctAnswers[i] == 1: # Correct answer: TRUE / YES
                    if answers[i] == 1: # User answered: TRUE / YES
                        graded.append(1)
                    else:  # User answered: False / NO
                        graded.append(0)

                else: # Correct answer: FALSE / NO
                    if answers[i] == 1: # User answered: TRUE / YES
                        graded.append(0)
                    else:  # User answered: False / NO
                        graded.append(1)

        elif problemType == "comparison":
            for i in range(len(answers)):

                if confidenceThreshold is not None:
                    if confidence[i] < confidenceThreshold: # Failed to pass confidence level test
                        graded.append(0) # Mark the answer wrong without checking the answer
                        continue

                if correctAnswers[i] == 0: # Correct answer: 1st item
                    if answers[i] == 1: # User answered: 1st item
                        graded.append(1)
                    else:  # User answered: 2nd item
                        graded.append(0)

                else: # Correct answer: 2nd item
                    if answers[i] == 1: # User answered: 1st item
                        graded.append(0)
                    else:  # User answered: 2nd item
                        graded.append(1)

        total = 0
        for g in graded:
            if g == 1:
                total += 1

        score = round(total / len(graded), 2)
        return score, graded

    def gradeHighVsLowLevelFeatures(self, featureGradedCL, featureGradedPWC, highLevel=True):
        graded = []

        for i in range(len(featureGradedCL)):
            add = False
            if highLevel:
                if FEATURE_CL_HIGH_LEVEL[i] == 1:
                    add = True
            else:
                # lowLevel
                if FEATURE_CL_HIGH_LEVEL[i] == 0:
                    add = True
            if add:
                graded.append(featureGradedCL[i])


        for i in range(len(featureGradedPWC)):
            add = False
            if highLevel:
                if FEATURE_PWC_HIGH_LEVEL[i] == 1:
                    add = True
            else:
                # lowLevel
                if FEATURE_PWC_HIGH_LEVEL[i] == 0:
                    add = True
            if add:
                graded.append(featureGradedCL[i])

        total = 0
        for g in graded:
            if g == 1:
                total += 1

        score = round(total / len(graded), 2)
        return score, graded

    def gradePositiveOrNegativeFeatures(self, featureGradedCL, featureGradedPWC, positive=True):
        graded = []
        for i in range(len(featureGradedCL)):
            problemParityPositive = None
            if FEATURE_CL_QUESTION_ANSWER[i] == 1:
                if FEATURE_CL_PARITY[i] == 1: # Paritiy is positive and the correct answer is True
                    problemParityPositive = True 
                else: # Paritiy is positive and the correct answer is False
                    problemParityPositive = False 
            else:
                if FEATURE_CL_PARITY[i] == 1: # Paritiy is negative and the correct answer is True
                    problemParityPositive = False 
                else: # Paritiy is positive and the correct answer is False
                    problemParityPositive = True 
        
            if positive == problemParityPositive:
                if featureGradedCL[i] == 1: # Correctly answered the question
                    graded.append(1)
                else:
                    graded.append(0)

        for i in range(len(featureGradedPWC)):
            problemParityPositive = None
            if FEATURE_PWC_PARITY[i] == 1:
                problemParityPositive = True
            else:
                problemParityPositive = False
        
            if positive == problemParityPositive:
                if featureGradedPWC[i] == 1: # Correctly answered the question
                    graded.append(1)
                else:
                    graded.append(0)

        total = 0
        for g in graded:
            if g == 1:
                total += 1

        score = round(total / len(graded), 2)
        return score, graded

