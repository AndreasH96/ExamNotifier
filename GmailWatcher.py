from __future__ import print_function
import pickle
import email
import base64
import os.path
import re
import csv
from datetime import date, datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from lib.Dataframes import timeedit_df
import pandas as pd
from lib.Mail import Mail

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

REMOVEUNREADLABEL = {"removeLabelIds": ["UNREAD"], "addLabelIds": []}
HHSTUDENTMAILDOMAIN = "student.hh.se"


class GmailWatcher:
    def __init__(self, markAsRead=False):
        self.markAsRead = markAsRead

        self.allowed_df = pd.read_csv("allowedUsers.csv")
        self.ownerEmails = pd.read_csv("owners.csv").userid.to_list()
        self.statusFunctions = {
            "NOT STUDENT": self.notStudent,
            "STATUS": self.studentStatus,
            "DELETE": self.deleteStudent,
            "INCORRECT": self.incorrectMail,
            "NEWUSERS": self.appendPersonsToAllowedList,
            "REMOVEUSERS": self.removePersonsFromAllowedList,
            "OK": self.appendNotification,
        }
        self.authorizeToGMailAPI()
        self.readInbox()

    def authorizeToGMailAPI(self):
        """
            Authorizes to the Gmail API, updating self.service
            Copied from Gmail tutorial courseCode
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        self.service = build("gmail", "v1", credentials=creds)

    def readInbox(self):
        """
            Reads the gmail inbox of the bot, then forwards the extracted data to the correct method
        """
        # Call the Gmail API, fetching the ids of unread emails from the inbox
        response = (
            self.service.users()
            .messages()
            .list(userId="me", q="to:exampickup@gmail.com")
            .execute()
        )

        unreadEmails = []

        # Append all unread emails to unreadEmails
        if "messages" in response:
            unreadEmails.extend(response["messages"])

        for email in unreadEmails:
            # Calling the Gmail API to fetch the data of the specific email
            receivedEmail = (
                self.service.users()
                .messages()
                .get(userId="me", id=email["id"], format="full")
                .execute()
            )

            # Extract the wanted action and data of the email
            status, emailData = self.extractEmailData(receivedEmail)

            # Call the Gmail API to mark the message as read if
            # the mail was successfully fetched and the markAsRead flag is set
            if emailData != None and self.markAsRead:
                self.service.users().messages().modify(
                    userId="me", id=email["id"], body=REMOVEUNREADLABEL
                ).execute()

            # Perform the desired action, show by the status parameter
            self.statusFunctions[status](emailData)

    def extractEmailData(self, receivedEmail):
        """
            Extracts the content of email and return the data.
            Checks so that the sender is a student at Halmstad University before extracting any data

            Input: gmail of full format fetched using the Gmail API.

            Returns: List of dictionaries with the following content
                * Student name
                * Student Email
                * Course courseCode
                * Flag for if sent exam registration mail to the student
                * Flag for if sent exam pickup mail to the student
                * Date of receiving the email from the student

            If the students mailed contained "Status" or "Delete", then the method will return "STATUS" or "DELETE".

            If the sender is not a student at Halmstad university, the method will return "NOT STUDENT".
        """

        # Extract the raw sender information from the correct email header
        emailHeaders = receivedEmail["payload"]["headers"]
        for header in emailHeaders:
            if header["name"] == "From":
                senderHeader = header["value"]
            elif header["name"] == "Subject":
                emailSubject = header["value"]

        # Use regex to find the name and email of the student
        try:
            # If person has åäö in name, they will have quotations around their name
            # Therefore needs more advanced regex

            # Jackiboys lösning
            parts = senderHeader.split("<")
            stripThings = ' "<>'
            senderName = parts[0].strip(stripThings)
            senderEmail = parts[1].strip(stripThings)
            senderEmailDomain = senderEmail.split("@")[1]

            # senderName = re.findall(r'(\w(.+?))((?="\s<)|(?=\s<))', senderHeader)[0][0]
            # senderEmail = re.findall(r"<(.+?)>", senderHeader)[0]
            # senderEmailDomain = re.findall(r"[^@]*$", senderEmail)[0]
        except Exception as e:
            errMsg = "incorrect email header: '{}'\n\n{}".format(senderHeader, e)
            return "INCORRECT", {"error": errMsg}

        # Checks so that the person who sends an email is a student at Halmstad University
        # If not student, return error message
        if senderEmailDomain != HHSTUDENTMAILDOMAIN:
            return "NOT STUDENT", {"name": senderName, "email": senderEmail}

        # Get current date and time to store when email was recieved
        timeReceived = datetime.today().date()

        # Only need the first rows, can therefore use ["snippet"] instead of getting the whole message
        # Snippet will have the content separated by spaces
        # Filtering out empy indices if there are any
        emailContent = list(filter(None, receivedEmail["snippet"].split(" ")))

        # If user sends course code in subject, append it to the email content
        subjectCourseCodes = re.findall(r"\D{2}\d{4}", emailSubject)
        emailContent.extend(subjectCourseCodes)

        # Admin commands, only performable by the owners
        if senderEmail in self.ownerEmails:
            adminCommand = emailSubject.replace(" ", "").lower()
            # Check if Admin wishes to add new users
            if adminCommand in ["newusers", "newstudents", "newuser", "newstudent"]:
                return "NEWUSERS", {"email": senderEmail, "users": emailContent}

            elif adminCommand in [
                "removeusers",
                "removestudents",
                "removeuser",
                "removestudent",
            ]:
                return "REMOVEUSERS", {"email": senderEmail, "users": emailContent}

        lines = [line.lower() for line in emailContent]

        for command in ["status", "delete"]:
            if command in lines or emailSubject.lower() == command:
                return command.upper(), {"name": senderName, "email": senderEmail}

        emailData = []
        time_df = timeedit_df()

        def calcExamWriteDate(mailTime, courseCode):
            # take the date of the exam that is closest in time
            examDates = time_df[time_df.courseCode == courseCode].examWriteDate.dt.date
            time_df["diff"] = abs(mailTime - examDates)

            closestInTime = time_df.sort_values(
                "diff", ascending=True
            ).examWriteDate.reset_index(drop=True)
            time_df.drop("diff", axis=1, inplace=True)

            if not closestInTime.empty:
                examWriteDate = closestInTime[0].date()
                return examWriteDate

            return None

        for courseCode in emailContent:
            # Iterate through the lines of the email
            # Checking so the input is correct with 2 Letters followed by 4 digits
            # Then turns the letters to upper case if the sender sent with lower case

            if len(re.findall(r"\D{2}\d{4}", courseCode)) != 0:
                examWriteDate = calcExamWriteDate(timeReceived, courseCode)
                if not examWriteDate:
                    # Exit early if a single course code wasn't found
                    errMsg = "courseCode '{}' not found".format(courseCode)
                    return "INCORRECT", {"error": errMsg}

                emailDataLine = {
                    "name": senderName,
                    "email": senderEmail,
                    "examWriteDate": examWriteDate,
                    "courseCode": courseCode.upper(),
                    "mailTime": timeReceived,
                    "firstRegistrationMail": False,
                    "lastRegistrationMail": False,
                    "collectMail": False,
                }

                emailData.append(emailDataLine)

            if len(emailData) == 0:
                return "INCORRECT", {"error": "No coursecodes"}

        return "OK", emailData

    def appendPersonsToAllowedList(self, emailData):
        """
            Appends the list of users to allowedUsers.csv

            Input: List of user emails to allow

        """

        newUsers = emailData["users"]

        # add the users to the dataframe
        self.allowed_df = self.allowed_df.append(
            [{"email": v} for v in newUsers], ignore_index=True
        )
        # we added those that are in newUsers and are not duplicated
        usersAdded = self.allowed_df[
            self.allowed_df.email.isin(newUsers)
            & ~self.allowed_df.duplicated(keep=False)
        ].to_list()

        # now, we drop the duplicates for good
        self.allowed_df.drop_duplicates(inplace=True)
        self.allowed_df.to_csv("allowedUsers.csv", index=False)

        # for newuser in newUsers:
        #     if not (self.allowed_df.isin([newuser]).any()).to_list()[0]:
        #         self.allowed_df = self.allowed_df.append(
        #             {"email": newuser}, ignore_index=True
        #         )
        #         usersAdded.append(newuser)

        # self.allowed_df.to_csv("allowedUsers.csv", index=False)

        if len(usersAdded) > 0:
            mailText = "Successfully added {} to allowedUsers.csv".format(usersAdded)

            self.infoMailAdmin(receiver=emailData["email"], mailText=mailText)

    def removePersonsFromAllowedList(self, emailData):
        """
            Removes the users in the list from allowedUsers.csv

            Input: List of user emails to remove

        """
        userEmailList = emailData["users"]
        mask = self.allowed_df.email.isin(userEmailList) & ~self.allowed_df.email.isin(
            self.ownerEmails
        )

        keep = self.allowed_df[~mask]
        usersRemoved = self.allowed_df[mask].email.to_list()

        # usersRemoved = []
        # for userEmail in userEmailList:
        #     if userEmail not in self.ownerEmails:
        #         # Get index of user
        #         result = self.allowed_df.index[
        #             self.allowed_df.email == userEmail
        #         ].tolist()
        #         if len(result) > 0:
        #             index = result[0]
        #             # Remove user if in allowed users
        #             self.allowed_df = self.allowed_df.drop([index])
        #             usersRemoved.append(userEmail)

        self.allowed_df = keep
        self.allowed_df.to_csv("allowedUsers.csv", index=False)

        if len(usersRemoved) > 0:
            mailText = "Successfully removed {} to allowedUsers.csv".format(
                usersRemoved
            )

            self.infoMailAdmin(receiver=emailData["email"], mailText=mailText)

    def appendNotification(self, emailData):
        """
            Appends the notification to the data storage.

            Input: Email data extracted by extractEmailData()

        """

        newDF = pd.DataFrame(emailData)
        state = pd.read_csv("lib/state.csv")

        newState = (
            pd.concat([state, newDF])
            .reset_index(drop=True)
            .drop_duplicates(ignore_index=True)
        )
        newState.to_csv("lib/state.csv", index=False)

    def studentStatus(self, senderNameAndEmail):
        print("STATUS for {}".format(senderNameAndEmail["email"]))

        state = pd.read_csv("lib/state.csv")
        rows = state[state.email == senderNameAndEmail["email"]]

        if rows.empty:
            msg = "Hi! The database doesn't have anything at all on you. Cheers!"

        else:
            msg = "Hello {}, here's what the database has about you.<br>{}<br>Cheers!".format(
                senderNameAndEmail["name"].split(" ")[0], rows.to_html()
            )

        mail = Mail(senderNameAndEmail["email"], msg)
        mail._send()

    def deleteStudent(self, senderNameAndEmail):
        print("DELETE for {}".format(senderNameAndEmail["email"]))
        state = pd.read_csv("lib/state.csv")
        mask = state[state.email == senderNameAndEmail["email"]]
        vask = state[mask]

        msg = "Deleted the following rows from the database: {}".format(vask.to_html())
        mail = Mail(senderNameAndEmail["email"], msg)
        mail._send()

        state[~mask].to_csv("lib/state.csv", index=False)

    def notStudent(self, senderNameAndEmail):
        print("NOT STUDENT '{}'".format(senderNameAndEmail["email"]))

        msg = "Hi! Your mail was not sent from the domain {}. This service exists solely for the".format(
            HHSTUDENTMAILDOMAIN
        )
        mail = Mail(senderNameAndEmail["email"], msg)
        mail._send()

    def incorrectMail(self, errDict):
        # don't respond to student about a server error
        msg = "INTERNAL SERVER ERROR '{}'".format(errDict["error"])
        print(msg)

    def infoMailAdmin(self, mailText, receiver=None):
        if receiver == None:
            receiver = self.ownerEmails[0]
        mail = Mail(receiver, mailText)
        mail._send()


gmailWatcher = GmailWatcher(markAsRead=False)

