from ExamScraper import ExamScraper
from Student import Student
from Exam import Exam

exams = [Exam("DT4015")]
student = Student(name="Andreas", email="",academy ="ITE",exams = exams)
examScraper = ExamScraper()
examData =examScraper.getExamDataFrame()
#print(examData)
studentExams = []
for exam in exams:
    examMask = examData.get("ITE")["Course_Code"] == exam
