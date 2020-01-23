import pandas as pd


def get_state_df():
    """
    Returns the current state as a dataframe.
    Columns: name,email,code,registrationMail,collectMail
    """

    state_df = pd.read_csv("state.csv", parse_dates=["mailTime", "examWriteDate"])
    return state_df


def write_state_df(df):
    df.to_csv("state.csv")

