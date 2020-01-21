from __future__ import print_function
import pickle
import email
import base64
import os.path
import re
from datetime import date,datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']
REMOVEUNREADLABEL = {'removeLabelIds': ['UNREAD'], 'addLabelIds': []}
HHSTUDENTMAILDOMAIN = "student.hh.se"

class GmailWatcher():
    def __init__(self):
        self.authorizeToGMailAPI()
        self.readInbox()


    def authorizeToGMailAPI(self):
        """
            Authorizes to the Gmail API, updating self.service
            Copied from Gmail tutorial code
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def readInbox(self):
        """
            Reads the gmail inbox of the bot and transmitts the data to a data file
        """
        # Call the Gmail API, fetching the ids of unread emails from the inbox
        response = self.service.users().messages().list(userId='me',q='to:exampickup@gmail.com is:unread').execute()
        unreadEmails = []

        # Append all unread emails to unreadEmails
        if 'messages' in response:
            unreadEmails.extend(response['messages'])

        for email in unreadEmails:
            # Calling the Gmail API to fetch the data of the specific email
            receivedEmail = self.service.users().messages().get(userId ='me', id=email["id"] ,format ="full").execute()

            emailData = self.extractEmailData(receivedEmail)

            #if emailData != None:
                # Call the Gmail API to mark the message as read
                #self.service.users().messages().modify(userId='me', id=email["id"], body = REMOVEUNREADLABEL).execute()
            
            if emailData == "NOT STUDENT":
                print("not student")

    def extractEmailData(self,receivedEmail):
        """
            Extracts the content of email and return the data.
            Checks so that the sender is a student at Halmstad University before extracting any data

            Input: gmail of full format fetched using the Gmail API.

            Returns: List of dictionaries with the following content
                * Student name
                * Student Email
                * Course code
                * Flag for if sent exam registration mail to the student
                * Flag for if sent exam pickup mail to the student
                * Date of receiving the email from the student

            If the students mailed contained "Status" or "Delete", then the method will return "STATUS" or "DELETE".

            If the sender is not a student at Halmstad university, the method will return "NOT STUDENT".
        """

        # Extract the raw sender information from the email headers
        senderHeader = receivedEmail["payload"]["headers"][17]["value"]

        # Use regex to find the name and email of the student
        senderName = re.findall(r'"(.+?)"', senderHeader)[0]
        senderEmail = re.findall(r'<(.+?)>',senderHeader)[0]
        
        senderEmailDomain = re.findall(r'[^@]*$',senderEmail)[0]
        
        
        # Checks so that the person who sends an email is a student at Halmstad University
        # If not student, return error message
        if senderEmailDomain != HHSTUDENTMAILDOMAIN:
            return "NOT STUDENT"

        
        # Get current date and time to store when email was recieved
        todaysTime = datetime.today()
        timeRecieved = "{} {}:{}".format(todaysTime.date(),todaysTime.hour,todaysTime.minute)
       
        # Only need the first rows, can therefore use ["snippet"] instead of getting the whole message
        # Snippet will have the content separated by spaces
        # Filtering out empy indices if there are any
        emailContent = list(filter(None,receivedEmail["snippet"].split(" ")))

      
        # Check if the student wishes to recieve a status
        if emailContent[0].lower() == "status":
            return "STATUS"

        # Check if the student wishes to be deleted from the database
        elif emailContent[0].lower() == "delete":
            return "DELETE"
        
        emailData = []

        for courseCode in emailContent:

            # Iterate through the lines of the email
            # Checking so the input is correct with 2 Letters followed by 4 digits
            # Then turns the letters to upper case if the sender sent with lower case

            if len(re.findall(r"\D{2}\d{4}", courseCode)) != 0:
                
                emailDataLine = {"name":senderName, "email":senderEmail,"code":courseCode,
                            "registrationMail":False,"collectMail":False,"mailTime":timeRecieved}

                emailData.append(emailDataLine)
        
        return emailData

        



    def studentStatus(self,senderEmail):
        pass

    def deleteStudent(self,senderEmail):
        pass
            

gmailWatcher = GmailWatcher()


