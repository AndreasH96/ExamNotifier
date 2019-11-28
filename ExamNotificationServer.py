from ExamScraper import ExamScraper
from Student import Student
from Exam import Exam
import json
from flask import Flask
from flask_mail import Mail
from flask_mail import Message
import pandas as pd
class ExamNotificationServer:
    def __init__(self):

        self.updateStudents()
        self.ExamScraper = ExamScraper()
        self.ExamDataFrame = self.ExamScraper.getExamDataFrame()

        with open("credentials.json") as credentials:
            self.credentials = json.load(credentials)
        with open("examMessage.json") as messageJSON:
            self.messageBase = json.load(messageJSON)["Message"]
        self.app = Flask("ExamNotifier")
        self.app.config['MAIL_SERVER']='smtp.gmail.com'  #Sendig using Googles mail server
        self.app.config['MAIL_PORT'] = 465
        self.app.config['MAIL_USERNAME'] = self.credentials["Email"]
        self.app.config["MAIL_PASSWORD"] = self.credentials["Password"]
        self.app.config['MAIL_USE_TLS'] = False
        self.app.config['MAIL_USE_SSL'] = True
        self.mail = Mail(self.app)


       
    def updateExamData(self):
        self.ExamDataFrame = self.ExamScraper.getExamDataFrame()

    def updateStudents(self):
        with open("students.json") as studentsJSON:
            self.studentsDict = json.load(studentsJSON)
            
    def addStudent(self,student):
        self.updateStudents()
        with open("students.json","w") as studentsJSONWrite:
            self.studentsDict["Students"].append(student.__dict__)
            json.dump(studentsDict,studentsJSONWrite)

    
exams = [{"CourseCode":"MA2043","Notified":False}]
student = Student(name="Andreas", email="andreashaggstrom96@gmail.com",academy ="ITE",exams = exams)
#addStudent(student)

examNotificationServer = ExamNotificationServer()
#print(examData)
#studentExams = []
for exam in exams:
    #print(examNotificationServer.ExamDataFrame.get("ITE")["Course_Code"])
    #print(examNotificationServer.ExamDataFrame.get("ITE")["Course_Code"])
    #print(type(examNotificationServer.ExamDataFrame.get("ITE")["Course_Code"]))
    #examMask = examNotificationServer.ExamDataFrame.get("ITE")["Course_Code"] == exam["CourseCode"]
    
    
    
    
   
    dataFrame = examNotificationServer.ExamDataFrame.get("ITE")
    examMask = dataFrame["Course_Code"] == "MA2043"
    print(type(examMask))
    examMask.where(examMask, dataFrame)
#print(examMask)

"""examNotificationServer = ExamNotificationServer()
with examNotificationServer.app.app_context():

    msg = Message("Hello",body=str(examNotificationServer.messageBase).format(student.name,student.exams[0]["CourseCode"],"Test"),
                    sender=examNotificationServer.credentials["Email"],
                    recipients=["andreashaggstrom96@gmail.com"])
    examNotificationServer.mail.send(msg)"""