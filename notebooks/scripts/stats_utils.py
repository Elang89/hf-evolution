import pandas as pd
import math

from scipy.stats import describe

def calculate_four_moments(dataframe: pd.DataFrame) -> pd.DataFrame:
    cols = ["Distribution", "Min", "Max", "Mean", "Std", "Skew", "Kurt"]
    vals = []
    for name, values in dataframe.iteritems():
        _, minmax, mean, variance, skewness, kurtosis = describe(values)
        curr_val = [name, minmax[0], minmax[1], mean, math.sqrt(variance), skewness, kurtosis]
        vals.append(curr_val)

    return pd.DataFrame(vals, columns=cols)

