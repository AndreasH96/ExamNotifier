#!/usr/bin/env python3

from lib.FirstRegistrationBot import FirstRegistrationBot
from lib.LastRegistrationBot import LastRegistrationBot
from lib.CollectBot import CollectBot

"""
Should be runned periodically, ideally once a day.
Sends out all mails that should be sent.
"""

LastRegistrationBot().sendMails()
FirstRegistrationBot().sendMails()
CollectBot().sendMails()
