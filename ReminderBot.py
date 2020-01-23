from Dataframes import openForRegistration_df


class ReminderBot(Bot):
    def __init__(self):
        super().__init__(self, df=openForRegistration_df(), booleanColumn="firstRegistrationMail")

    def getMsg(self, row):
        f"Hi {row['name'].split(' ')[0]}! You can now register for {row['code']} on Ladok. Good luck!"
