from lib.Dataframes import openForRegistration_df
from lib.Bot import Bot
from datetime import datetime, timedelta


class LastRegistrationBot(Bot):
    def __init__(self):
        super().__init__(openForRegistration_df(), "lastRegistrationMail")
        self.today = datetime.today()

    def df_filter(self, df):
        lastMail = self.today.date() == df["registrationEnd"].dt.date - timedelta(
            days=1
        )
        # keep rows where lastMail is true
        return df[lastMail]

    def getMsg(self, row):
        return f"Hi {row['name'].split(' ')[0]}. Tomorrow is the last day to register for {row['courseCode']}. Don't sleep, be an agent."
