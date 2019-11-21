from ExamScraper import ExamScraper
from Student import Student
from Exam import Exam
import json

def getStudents():
    with open("ExamNotifier\students.json") as studentsJSON:
        studentsDict = json.load(studentsJSON)["Students"]
    return studentsDict
def addStudent(student):
    studentJSONFormat= {"name":student.name, "email":student.email,"academy" :student.academy,"exams":  student.exams}
    with open("ExamNotifier\students.json") as studentsJSON:
        studentsDict = json.load(studentsJSON)["Students"]
    with open("ExamNotifier\students.json","w") as studentsJSONWrite:
        studentsDict.append(studentJSONFormat)
        json.dump(studentsDict,studentsJSONWrite)

    
exams = [{"CourseCode":"DT4012","Notified":False}]
student = Student(name="Andreas", email="@gmail.com",academy ="ITE",exams = exams)
addStudent(student)
examScraper = ExamScraper()
examData =examScraper.getExamDataFrame()
#print(examData)
studentExams = []
for exam in exams:
    examMask = examData.get("ITE")["Course_Code"] == exam
