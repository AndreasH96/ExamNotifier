from lib.Dataframes import collect_df
from lib.Bot import Bot


class CollectBot(Bot):
    def __init__(self):
        super().__init__(collect_df(), "collectMail")

    def getMsg(self, row):
        return f"Hi {row['name'].split(' ')[0]}. You can collect your exam now in {row.courseName} ({row.courseCode}) that you wrote {row.examWriteDate.date()}."
        # return f"Hello dear {row['name'].split(' ')[0]}. The exam {row.courseName} is now at Service Center and ready to be picked up! Hope it went well!"
