from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re

import os
from datetime import datetime
import locale

locale.setlocale(locale.LC_ALL, "sv_SE.utf8")

dir_path = os.path.dirname(os.path.realpath(__file__))


def collect_df():
    """
    Returns a dataframe with info for collecting your exam.
    Columns: examWriteDate, courseCode, courseName, teacher, examType
    """

    with open(dir_path + "/../data/collect.html") as f:
        html = f.read()

    bs = BeautifulSoup(html, features="lxml")
    arr = [i.text for i in bs.find_all("td")]
    # group each four elements into one row
    df = pd.DataFrame(
        pd.Series(arr).values.reshape((-1, 4)),
        columns=["examWriteDate", "courseCode", "courseName", "teacher"],
    )

    def splitcourseCode(x):
        # FÖ2014: 2 characters and 4 digits
        x["courseCode"] = re.findall(r"\D{2}\d{4}", x["courseCode"])
        return x

    # "2019-11-15Dugga" => Datum: 2019-11-15, examType: Dugga
    df[["examWriteDate", "examType"]] = (
        df.examWriteDate.str.strip()
        .str.title()
        .str.extract(r"(\d{4}-\d{2}-\d{2})(\S+)?", expand=True)
    )

    # If type is unknown, just say "Tenta"
    df.examType.fillna("Tenta", inplace=True)

    # split duplicate courseCode, duplicating the other values
    df = df.apply(splitcourseCode, axis=1).explode("courseCode").reset_index(drop=True)
    df.examWriteDate = pd.to_datetime(df.examWriteDate)
    return df


def signup_df():
    """
    Returns a dataframe with info about when you can sign up for exams.
    """
    with open(dir_path + "/../data/tentor.html") as f:
        data = f.read()

    bs = BeautifulSoup(data, features="lxml")
    ser = pd.Series(
        [li.text for li in bs.find_all("li") if li.find("strong", recursive=False)]
    )
    year = re.findall(r"Anmälningstider .+? (\d{4})", bs.text)[0]

    df = pd.DataFrame(
        ser.str.split(":").explode().values.reshape(-1, 2),
        columns=["examWeek", "registration"],
    )
    df.examWeek = df.examWeek.str.split("vecka ").apply(lambda x: x[1])

    def splitExamWeek(x):
        x["examWeek"] = re.findall(r"\d{1,2}", x["examWeek"])
        return x

    def timeSpan(x):
        return [datetime.strptime(f"{v} {year}", "%d %B %Y") for v in x.split("–")]

    df = df.apply(splitExamWeek, axis=1).explode("examWeek").reset_index(drop=True)
    df.examWeek = df.examWeek.astype(int)
    df[["registrationStart", "registrationEnd"]] = pd.DataFrame(
        df["registration"].str.strip().apply(timeSpan).explode().values.reshape(-1, 2),
        columns=["Start", "End"],
    )
    df.drop("registration", axis=1, inplace=True)

    # df["totalTime"] = df["registrationEnd"] - df["registrationStart"]
    return df


def timeedit_df():
    """
    Returns a dataframe with info about current exams running.
    """
    df = pd.read_csv(dir_path + "/../data/timeedit.csv", skiprows=3)
    df.rename(
        columns={
            "Startdatum": "examWriteDate",
            "Starttid": "examWriteTime",
            "Slutdatum": "endDate",
            "Sluttid": "endTime",
            "Klass,Kurstillfälle": "misc",
            "Lokal": "place",
            "Lärare": "teacher",
            "Undervisningstyp": "examType",
            "Status": "status",
            "Kommentar": "comment",
            "Provkod": "testCode",
        },
        inplace=True,
    )

    def splitCourseCode(x):
        # FÖ2014: 2 characters and 4 digits
        x["courseCode"] = re.findall(r"\D{2}\d{4}", x["misc"])
        return x

    for c in ["examWriteDate", "endDate"]:
        df[c] = pd.to_datetime(df[c])

    # `courseCode` och `examWeek som går att anmäla sig`.

    df = df.apply(splitCourseCode, axis=1).explode("courseCode").reset_index(drop=True)
    df["examWeek"] = df["examWriteDate"].dt.week
    df.drop_duplicates(inplace=True)
    return df


def openForRegistration_df():
    """
    Return a dataframe where you can calculate which exams that are open for registration right now.
    """
    sdf = signup_df()
    tdf = timeedit_df()
    big_df = tdf.merge(sdf, on="examWeek", how="inner")
    return big_df


if __name__ == "__main__":
    print(openForRegistration_df())
