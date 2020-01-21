from ExamScraper import ExamScraper
from Student import Student
from Exam import Exam
import json
from flask import Flask
from flask_mail import Mail
from flask_mail import Message
import pandas as pd

class EmailSender():
    def __init__(self):

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


       
    

    
exams = [{"CourseCode":"MA2043","Notified":False}]
student = Student(name="Andreas", email="andreashaggstrom96@gmail.com",academy ="ITE",exams = exams)
#addStudent(student)

emailSender = EmailSender()

"examNotificationServer = ExamNotificationServer()
with examNotificationServer.app.app_context():

    msg = Message("Hello",body=str(examNotificationServer.messageBase).format(student.name,student.exams[0]["CourseCode"],"Test"),
                    sender=examNotificationServer.credentials["Email"],
                    recipients=["andreashaggstrom96@gmail.com"])
    examNotificationServer.mail.send(msg)