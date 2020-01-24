from __future__ import print_function
import pickle
import email
import base64
import os.path
import re
from datetime import date, datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from Dataframes import timeedit_df

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

REMOVEUNREADLABEL = {"removeLabelIds": ["UNREAD"], "addLabelIds": []}
HHSTUDENTMAILDOMAIN = "student.hh.se"


class GmailWatcher:
    def __init__(self, markAsRead=False):
        self.markAsRead = markAsRead
        # used to keep users from spamming the bot
        self.bannedUsers = []
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
            if status == "NOT STUDENT":
                self.notStudent(emailData)

            elif status == "STATUS":
                self.studentStatus(emailData)

            elif status == "DELETE":
                self.deleteStudent(emailData)

            elif status == "NO COURSECODES":
                self.incorrectMail(emailData)

            elif status == "NORMAL":
                print(emailData)
                self.appendNotification(emailData)

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

        # Use regex to find the name and email of the student
        try:
            # If person has åäö in name, they will have quotations around their name
            # Therefore needs more advanced regex
            senderName = re.findall(r'(\w(.+?))((?="\s<)|(?=\s<))', senderHeader)[0][0]
            # senderName = re.findall(r'"(.+?)"', senderHeader)[0]
        except:
            senderName = "Error"
        try:
            senderEmail = re.findall(r"<(.+?)>", senderHeader)[0]
        except:
            senderEmail = "Error"
        try:
            senderEmailDomain = re.findall(r"[^@]*$", senderEmail)[0]
        except:
            senderEmailDomain = "Error"

        # Checks so that the person who sends an email is a student at Halmstad University
        # If not student, return error message
        if senderEmailDomain != HHSTUDENTMAILDOMAIN:
            return "NOT STUDENT", {"name": senderName, "email": senderEmail}

        # Check if user is banned from the service
        elif senderEmailDomain in self.bannedUsers:
            return "BANNED USER", {"name": senderName, "email": senderEmail}

        # Get current date and time to store when email was recieved
        todaysTime = datetime.today()
        timeRecieved = "{} {}:{}".format(
            todaysTime.date(), todaysTime.hour, todaysTime.minute
        )

        # Only need the first rows, can therefore use ["snippet"] instead of getting the whole message
        # Snippet will have the content separated by spaces
        # Filtering out empy indices if there are any
        emailContent = list(filter(None, receivedEmail["snippet"].split(" ")))

        # Check if the student wishes to recieve a status
        if emailContent[0].lower() == "status":
            return "STATUS", {"name": senderName, "email": senderEmail}

        # Check if the student wishes to be deleted from the database
        elif emailContent[0].lower() == "delete":
            return "DELETE", {"name": senderName, "email": senderEmail}

        emailData = []
        time_df = timeedit_df()

        def calcExamWriteDate(mailTime, courseCode):
            # take the date of the exam that is closest in time
            time_df["diff"] = abs(mailTime - time_df[time_df.courseCode == courseCode].examWriteDate)
            tmp = time_df.sort_values("diff", ascending=True).examWriteDate.reset_index(
                drop=True
            )
            time_df.drop("diff", axis=1, inplace=True)

            if not tmp.empty:
                examWriteDate = tmp[0].date()
                return examWriteDate

            return None

        for courseCode in emailContent:
            # Iterate through the lines of the email
            # Checking so the input is correct with 2 Letters followed by 4 digits
            # Then turns the letters to upper case if the sender sent with lower case

            if len(re.findall(r"\D{2}\d{4}", courseCode)) != 0:
                examWriteDate = calcExamWriteDate(timeReceived, courseCode)
                if not examWriteDate:
                    print('ERR: Course courseCode "{}" not found'.format(courseCode))
                    continue

                emailDataLine = {
                    "name": senderName,
                    "email": senderEmail,
                    "courseCode": courseCode.upper(),
                    "registrationMail": False,
                    "collectMail": False,
                    "mailTime": timeRecieved,
                    "examWriteDate": examWriteDate
                }

                emailData.append(emailDataLine)

            if len(emailData) == 0:
                return "NO COURSECODES", {"name": senderName, "email": senderEmail}

        return "NORMAL", emailData

    def appendNotification(self, emailData):
        """
            Appends the notification to the data storage.

            Input: Email data extracted by extractEmailData()

            TODO: implement the appending of notification
        """
        pass

    def studentStatus(self, senderNameAndEmail):
        """
            TODO: implement sending the student the status
        """
        print("STATUS")

    def deleteStudent(self, senderNameAndEmail):
        """
            TODO: implement deleting student from data set
        """
        print("DELETE")

    def notStudent(self, senderNameAndEmail):
        """
            TODO: implement responding to student if we want to do that
        """
        print("NOT STUDENT")

    def incorrectMail(self, senderNameAndEmail):
        """
            TODO: implement responding(?) to the student
        """
        print("INCORRECT MAIL")


gmailWatcher = GmailWatcher(markAsRead=False)

