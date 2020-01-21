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
    Columns: Tentadatum, Kurskod, Kursnamn, Lärare, Typ
    """

    with open(dir_path + "/data/collect.html") as f:
        html = f.read()

    bs = BeautifulSoup(html, features="lxml")
    arr = [i.text for i in bs.find_all("td")]
    # group each four elements into one row
    df = pd.DataFrame(
        pd.Series(arr).values.reshape((-1, 4)),
        columns=["Tentadatum", "Kurskod", "Kursnamn", "Lärare"],
    )

    def splitKurskod(x):
        # FÖ2014: 2 characters and 4 digits
        x["Kurskod"] = re.findall(r"\D{2}\d{4}", x["Kurskod"])
        return x

    # "2019-11-15Dugga" => Datum: 2019-11-15, Typ: Dugga
    df[["Tentadatum", "Typ"]] = (
        df.Tentadatum.str.strip()
        .str.title()
        .str.extract(r"(\d{4}-\d{2}-\d{2})(\S+)?", expand=True)
    )

    # If type is unknown, just say "Tenta"
    df.Typ.fillna("Tenta", inplace=True)

    # split duplicate kurskod, duplicating the other values
    df = df.apply(splitKurskod, axis=1).explode("Kurskod").reset_index(drop=True)
    df.Tentadatum = pd.to_datetime(df.Tentadatum)
    return df


def signup_df():
    """
    Returns a dataframe with info about when you can sign up for exams.
    Columns: Tentavecka, AnmälanStart, AnmälanSlut, TotalTid
    """
    with open(dir_path + "/data/tentor.html") as f:
        data = f.read()

    bs = BeautifulSoup(data, features="lxml")
    ser = pd.Series(
        [li.text for li in bs.find_all("li") if li.find("strong", recursive=False)]
    )
    year = re.findall(r"Anmälningstider .+? (\d{4})", bs.text)[0]

    df = pd.DataFrame(
        ser.str.split(":").explode().values.reshape(-1, 2),
        columns=["Tentavecka", "Anmälan"],
    )
    df.Tentavecka = df.Tentavecka.str.split("vecka ").apply(lambda x: x[1])

    def splitTentavecka(x):
        x["Tentavecka"] = re.findall(r"\d{1,2}", x["Tentavecka"])
        return x

    def timeSpan(x):
        return [datetime.strptime(f"{v} {year}", "%d %B %Y") for v in x.split("–")]

    df = df.apply(splitTentavecka, axis=1).explode("Tentavecka").reset_index(drop=True)
    df.Tentavecka = df.Tentavecka.astype(int)
    df[["AnmälanStart", "AnmälanSlut"]] = pd.DataFrame(
        df["Anmälan"].str.strip().apply(timeSpan).explode().values.reshape(-1, 2),
        columns=["Start", "Slut"],
    )
    df.drop("Anmälan", axis=1, inplace=True)
    df["TotalTid"] = df["AnmälanSlut"] - df["AnmälanStart"]
    return df


def timeedit_df():
    """
    Returns a dataframe with info about current exams running.
    Columns: Kurskod, Tentavecka, Tentadatum, Lokal, Undervisningstyp, Status
    """
    df = pd.read_csv(dir_path + "/data/timeedit.csv", skiprows=3)

    def splitKurskod(x):
        # FÖ2014: 2 characters and 4 digits
        x["Kurskod"] = re.findall(r"\D{2}\d{4}", x["Klass,Kurstillfälle"])
        return x

    for c in ["Startdatum", "Slutdatum"]:
        df[c] = pd.to_datetime(df[c])

    # `Kurskod` och `Tentavecka som går att anmäla sig`.

    df = df.apply(splitKurskod, axis=1).explode("Kurskod").reset_index(drop=True)
    df["Vecka"] = df.Startdatum.dt.week
    df.rename(columns={"Vecka": "Tentavecka", "Startdatum": "Tentadatum"}, inplace=True)
    df.drop_duplicates(inplace=True)
    df = df[
        ["Kurskod", "Tentavecka", "Tentadatum", "Lokal", "Undervisningstyp", "Status"]
    ]
    return df


def openForRegistration_df():
    """
    Return a dataframe where you can calculate which exams that are open for registration right now.
    Columns: Kurskod, Tentavecka, Tentadatum, Lokal, Undervisningstyp, Status, AnmälanStart, AnmälanSlut, TotalTid
    """
    sdf = signup_df()
    tdf = timeedit_df()
    big_df = tdf.merge(sdf, on="Tentavecka", how="inner")
    return big_df


if __name__ == "__main__":
    print(openForRegistration_df())
