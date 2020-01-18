from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re


def html2df(html):
    """
    Converts HTML tenta page to a pandas dataframe.
    """

    bs = BeautifulSoup(html, features="lxml")
    arr = [i.text for i in bs.find_all("td")]
    # group each four elements into one row
    df = pd.DataFrame(
        pd.Series(arr).values.reshape((-1, 4)),
        columns=["Datum", "Kurskod", "Kursnamn", "Lärare"],
    )

    def splitKurskod(x):
        # FÖ2014: 2 characters and 4 digits
        x["Kurskod"] = re.findall(r"\D{2}\d{4}", x["Kurskod"])
        return x

    # "2019-11-15Dugga" => Datum: 2019-11-15, Typ: Dugga
    df[["Datum", "Typ"]] = (
        df.Datum.str.strip()
        .str.title()
        .str.extract(r"(\d{4}-\d{2}-\d{2})(\S+)?", expand=True)
    )

    # If type is unknown, just say "Tenta"
    df.Typ.fillna("Tenta", inplace=True)

    # split duplicate kurskod, duplicating the other values
    df = df.apply(splitKurskod, axis=1).explode("Kurskod").reset_index(drop=True)
    return df
