from state import get_state_df
from Mail import Mail


class Bot:
    """
    Superclass for collectBot and submitBot.
    Logic that is in both of is the selection from their respective dataframes.
    The datasets are not the same, but should have a subset of common columns.
    Sending mails is the same in both.

    What's different in the bots is how they format their message. Therefore,
    getBody is an abstract method.
    """

    def __init__(self, df, booleanColumn):
        """
        df should be a dataframe from either collect_df or signup_df.
        """
        self.df = df
        self.booleanColumn = booleanColumn
        self.state_df = get_state_df()

    def sendMails(self):
        # sends the actual mails that should be sent!!!!
        mails = self.getMails()
        for mail in mails:
            mail._send()

    def getMails(self):
        """
        Internal method used to select relevant rows and wrap getMsg in a HTML-template. We should match both code and examWriteDate.

        Returns a list of Mails.
        """
        tmp_df = self.state_df.merge(
            self.df,
            left_on=["code", "examWriteDate"],
            right_on=["Kurskod", "Tentadatum"],
        )
        # keep only those rows that have not already been mailed
        tmp_df = tmp_df[~tmp_df[self.booleanColumn]]
        newDf = tmp_df.apply(self.getMsg, axis=1)
        return [Mail(*i) for i in newDf[["body", "email"]]]

    def getMsg(self, selected_rows_df):
        """
        Is called on each row.
        Should return a row with the column "body" and "email".
        """
        raise NotImplementedError
