from Dataframes import openForRegistration_df
from Bot import Bot


class FirstRegistrationBot(Bot):
    def __init__(self):
        super().__init__(openForRegistration_df(), "firstRegistrationMail")

    def getMsg(self, row):
        return f"Hi {row['name'].split(' ')[0]}. You can now register for {row['courseCode']} on Ladok. Have a nice day."
