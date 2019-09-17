
FEATURE_CL_QUESTION_ANSWER = [0, 1, 1, 1, 0, 0, 1, 0, 1]
FEATURE_PWC_QUESTION_ANSWER = [1, 0, 1, 0, 1, 1, 1, 0, 0]
DESIGN_CL_QUESTION_ANSWER = [1, 0, 0, 1, 1, 0, 1, 0, 1]
DESIGN_PWC_QUESTION_ANSWER = [1, 0, 0, 1, 1, 0, 0, 0, 1]

class Grader():
    def __init__(self, confidenceThreshold=None):
        self.confidenceThreshold = confidenceThreshold

    def setConfidenceThreshold(self, confidenceThreshold):
        self.confidenceThreshold = confidenceThreshold

    def gradeAnswers(self, problemTopic, problemType, answers, confidence=None):
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

                if self.confidenceThreshold is not None:
                    if confidence[i] < self.confidenceThreshold: # Failed to pass confidence level test
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

                if self.confidenceThreshold is not None:
                    if confidence[i] < self.confidenceThreshold: # Failed to pass confidence level test
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
