from FirstRegistrationBot import FirstRegistrationBot
from LastRegistrationBot import LastRegistrationBot
from CollectBot import CollectBot

"""
Should be runned periodically. Sends out all mails that should be sent.
"""
LastRegistrationBot().sendMails()
FirstRegistrationBot().sendMails()
CollectBot().sendMails()
