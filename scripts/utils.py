import numpy as np
import pandas as pd
import re

def money_to_int(x):
    if pd.isna(x):
        return np.nan

    if isinstance(x, (int, float)):
        return x

    x = str(x).replace("€","").replace(",","").lower()

    if "m" in x:
        return float(x.replace("m","")) * 1_000_000
    if "k" in x:
        return float(x.replace("k","")) * 1_000

    return float(x)

def percent_to_float(x):
    if pd.isna(x):
        return np.nan

    if isinstance(x, str) and "%" in x:
        return float(x.replace("%","")) / 100

    return x

def minutes_to_int(x): #removes min and return the value as int
    if isinstance(x, str):
        nums = re.findall(r'\d+', x)
        return int(nums[0]) if nums else np.nan
    return x


def replace_labels(x):
    if x in ["No Assists","No Pens"]:
        return 0
    return x

def clean_dataframe(df):

    df["Market Value"] = df["Market Value"].apply(money_to_int)
    df["Annual Salary"] = df["Annual Salary"].apply(money_to_int)

    percent_cols = [
        "Pass Completion Rate",
        "Dribble Success Rate",
        "Cross Completion Rate",
        "Save Percentage (Per90)"
    ]

    for col in percent_cols:
        df[col] = df[col].apply(percent_to_float)

    minute_cols = [
        "Minutes Per Goal",
        "Minutes Per Booking"
    ]

    for col in minute_cols:
        df[col] = df[col].apply(minutes_to_int)

    nos_cols =[
        "Penalty Conversion Rate",
        "Minutes Per Assist"
    ]
    for col in nos_cols:
        df[col]=df[col].apply(replace_labels)
    return df