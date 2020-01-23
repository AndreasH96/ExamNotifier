import pandas as pd


def get_state_df():
    """
    Returns the current state as a dataframe.
    Columns: name,email,code,registrationMail,collectMail
    """

    state_df = pd.read_csv("state.csv")
    state_df.mailTime = pd.to_datetime(state_df.mailTime)
    return state_df

def write_state_df(df):
    df.to_csv('state.csv')