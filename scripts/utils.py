import numpy as np
import pandas as pd
import re

def money_to_int(x):
    if pd.isna(x): return np.nan
    x = x.replace("€","").replace("m","")
    return float(x) * 1_000_000

def percent_to_float(x):
    if isinstance(x, str) and "%" in x:
        return float(x.replace("%","")) / 100
    return np.nan

def minutes_to_int(x):
    if isinstance(x, str):
        nums = re.findall(r'\d+', x)
        return int(nums[0]) if nums else np.nan
    return x