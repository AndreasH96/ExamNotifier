from state import get_state_df, set_state_df
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
            print(
                "Now sending {} to {}:\n{}\n-----".format(
                    self.booleanColumn, mail.email, mail.body
                )
            )
            mail._send()

    def df_filter(self, df):
        """
        Is called in getMails. Modify this in a child class to
        make mutations on self just before getMails returns.

        By default, this does nothing
        """
        return df

    def getMails(self):
        """
        Internal method used to select relevant rows and wrap getMsg in a HTML-template.
        Returns a list of Mails.
        """

        key_cols = ["courseCode", "examWriteDate"]
        tmp_df = self.state_df.merge(self.df, on=key_cols)
        # keep only those rows that have not already been mailed
        tmp_df = tmp_df[~tmp_df[self.booleanColumn]]

        # run through filter
        tmp_df = self.df_filter(tmp_df)

        # if empty, return empty list
        if tmp_df.empty:
            return []

        tmp_df["body"] = tmp_df.apply(self.getMsg, axis=1)

        # Also marks the correct values in state.csv to True
        shouldMailTo = tmp_df[key_cols + ["email"]]
        for i in shouldMailTo.iterrows():
            mask = (i[1] == self.state_df[key_cols + ["email"]]).all(axis=1)
            self.state_df.loc[mask, self.booleanColumn] = True

        set_state_df(self.state_df)

        return [Mail(*i[1:]) for i in list(tmp_df[["email", "body"]].itertuples())]

    def getMsg(self, selected_rows_df):
        """
        Is called on each row. Should return a string
        """
        raise NotImplementedError
