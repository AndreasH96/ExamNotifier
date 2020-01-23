from Dataframes import collect_df


class CollectBot(Bot):
    def __init__(self):
        super().__init__(self, collect_df())

    def getBody(self):
        pass
