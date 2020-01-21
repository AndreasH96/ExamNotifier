from Dataframes import collect_df
from state import get_state_df
import pandas as pd

# this script should be run periodically.


def collectMails():
    """
    Returns a dataframe with everything ready to just mail it away.
    Columns: code, name, email, mailTime, registrationMail, collectMail, Tentadatum, Kurskod, Kursnamn, Lärare, Typ, closeness, Body
    """

    coll_df = collect_df()
    state_df = get_state_df()

    # keep rows that have not already been sent
    df = state_df[~state_df.registrationMail]
    df = df.merge(coll_df, left_on="code", right_on="Kurskod", how="inner")
    df["code"] = df.Kurskod
    df["closeness"] = df.Tentadatum - df.mailTime
    df.sort_values("closeness", ascending=False, inplace=True)
    df = df.groupby(["code", "name"], as_index=False).first()

    def generateMsg(row):
        """Called by df.apply on each row.
        You can swap out this part to a HTML-generating thingie
        """
        return f"Hi {row['name'].split(' ')[0]}! You can collect your {row.Typ} in {row.code} ({row.Kursnamn[0]}) from {row.Tentadatum.date()} now."

    df["Body"] = df.apply(generateMsg, axis=1)

    # we need to set the registrationMail to True for all rows that we return.
    tmp = (
        df[state_df.columns].sort_values(list(state_df.columns)).reset_index(drop=True)
    )
    tmp2 = state_df.sort_values(list(state_df.columns)).reset_index(drop=True)
    selectedRows = tmp[tmp == tmp2]
    selectedRows["registrationMail"] = True

    # write dataframe to disk, should really be done in sendMail instead.
    # selectedRows.to_csv('state.csv')
    return df
