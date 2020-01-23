from Dataframes import collect_df


class CollectBot(Bot):
    def __init__(self):
        super().__init__(self, df=collect_df(), booleanColumn="collectMail")

    def getMsg(self, row):
        # return f"Hi {row['name'].split(' ')[0]}! You can collect your {row.Typ} in {row.code} ({row.Kursnamn[0]}) written {row.Tentadatum.date()} now in Service Center."
        return f"Hello dear {row['name'].split(' ')[0]}. The exam {row.Kursnamn} is now at Service Center and ready to be picked up! Hope it went well!"

        # f"Hi {row['name'].split(' ')[0]}! Tomorrow is the last day to register for {row['code']}. Good luck!"
