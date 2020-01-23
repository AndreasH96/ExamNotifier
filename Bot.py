class Bot:
    """
    Superclass for collectBot and submitBot.
    Logic that is in both of is the selection from their respective dataframes.
    The datasets are not the same, but should have a subset of common columns.
    Sending mails is the same in both.

    What's different in the bots is how they format their message. Therefore,
    getBody is an abstract method.
    """

    def __init__(self, data):
        """
        Data should be a dataframe from either
        collect_df or signup_df.
        """
        self.data = data

    def _selection(self):
        """
        Internal method used for selecting relevant rows from self.data
        """
        pass

    def getBody(self):
        raise NotImplementedError
