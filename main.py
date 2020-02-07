#!/usr/bin/env python3

from lib.FirstRegistrationBot import FirstRegistrationBot
from lib.LastRegistrationBot import LastRegistrationBot
from lib.CollectBot import CollectBot

"""
Should be runned periodically, ideally once a day.
Sends out mails about:

    - Registration for the first time
    - Registration for the last day
    - You can now collect your exam
"""

FirstRegistrationBot().sendMails()
LastRegistrationBot().sendMails()
CollectBot().sendMails()
