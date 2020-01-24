import pandas as pd
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_state_df():
    """
    Returns the current state as a dataframe.
    Columns: name,email,courseCode,registrationMail,collectMail
    """

    state_df = pd.read_csv(
        dir_path + "/state.csv", parse_dates=["mailTime", "examWriteDate"]
    )
    return state_df


def set_state_df(df):
    df.to_csv(dir_path + "/state.csv", index=False)

