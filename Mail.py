from string import Template
from email.mime.text import MIMEText
from string import Template
from email.mime.multipart import MIMEMultipart
import smtplib
import imaplib
import ssl
import time

# template wraps a body string in HTML
with open("mail_template.html") as f:
    template_str = f.read()


def render_mail(body):
    return Template(template_str).safe_substitute(body=body)


class Mail:
    def __init__(self, email, body):
        self.email = email
        self.body = body
        self.html = render_mail(body)

    def _send(self):
        """
        Sends this email to the intended recipident.
        """
        sender_email = "examnotifier@gmail.com"
        receiver_email = self.email
        password = "tjenis"  # andreas, fixa det här

        message = MIMEMultipart("alternative")
        message["Subject"] = "multipart test"
        message["From"] = sender_email
        message["To"] = receiver_email

        text = self.body
        html = self.html

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        # also copy that email to Sent
        imap = imaplib.IMAP4_SSL("imap.google.com", 993)
        imap.login(sender_email, password)
        imap.append(
            "INBOX.Sent",
            "\\Seen",
            imaplib.Time2Internaldate(time.time()),
            message.as_string().encode("utf8"),
        )
        imap.logout()

