import pandas as pd
import math

from scipy.stats import describe

import statsmodels.api as sm
import numpy as np

from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import het_white, het_arch
from typing import Dict, Tuple
from arch import arch_model
from random import seed

# TODO: Add Critical Values for tests

def calculate_four_moments(dataframe: pd.DataFrame) -> pd.DataFrame:
    cols = ["Distribution", "Min", "Max", "Mean", "Std", "Skew", "Kurt"]
    vals = []
    for name, values in dataframe.iteritems():
        _, minmax, mean, variance, skewness, kurtosis = describe(values)
        curr_val = [name, minmax[0], minmax[1], mean, math.sqrt(variance), skewness, kurtosis]
        vals.append(curr_val)

    return pd.DataFrame(vals, columns=cols)


def fix_holes(time_dataframe: pd.DataFrame) -> Tuple[pd.DataFrame, int, float]:
    downsampled = time_dataframe.resample(rule="D").mean()
    interpolated = downsampled.interpolate(method="polynomial", order=2)
    nan_count = downsampled.isna().sum()
    total_observations = downsampled.shape[0]
    missing_pct = np.round((nan_count / total_observations), 4) * 100

    return (downsampled, interpolated, total_observations, nan_count, missing_pct)

def adf(dataframe: pd.DataFrame, column: str) -> Tuple[float, float, Dict[str, float]]: 
    X = dataframe[column]
    result = adfuller(X)

    return (result[0], result[1], result[4])

def kpss_test(dataframe: pd.DataFrame, column: str) -> Tuple[float, float, Dict[str, float]]:
    X = dataframe[column]
    result = kpss(X)

    return (result[0], result[1], result[3]) 

def white(dataframe: pd.DataFrame, column: str) -> Tuple[float, float, float, float]:
    y = (dataframe.index - dataframe.index.min())  / np.timedelta64(1,'D')
    X = dataframe[column]

    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    result = het_white(model.resid, model.model.exog)

    return result

def arch_test(dataframe: pd.DataFrame, column: str) -> Tuple[float, float, float, float]:
    y = (dataframe.index - dataframe.index.min())  / np.timedelta64(1,'D')
    X = dataframe[column]

    model = sm.OLS(y, X).fit()

    result = het_arch(model.resid)

    return result

def create_tests_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "Time Series", 
        "ADF Statistic", 
        "ADF P-Value", 
        "KPSS Statistic", 
        "KPSS P-Value",
        "White T Statistic", 
        "White P-Value",
        "White F Statistic",
        "White FP-Value",
        "ARCH Lagrange Multiplier",
        "ARCH P-Value",
        "ARCH F Statistic",
        "ARCH FP-Value "
    ]
    values = []


    for name, _ in dataframe.iteritems():
        adf_statistic, adf_p, _,  = adf(dataframe, name)
        kpss_statistic, kpss_p, _ = kpss_test(dataframe, name)
        white_statistic, white_p, white_fstatistic, white_fp = white(dataframe, name)
        arch_statistic, arch_p, arch_fstatistic, arch_fp = arch_test(dataframe, name)

        curr_val = [
            name, 
            adf_statistic, 
            adf_p, 
            kpss_statistic, 
            kpss_p,
            white_statistic, 
            white_p, 
            white_fstatistic, 
            white_fp,
            arch_statistic,
            arch_p,
            arch_fstatistic, 
            arch_fp
        ]
        values.append(curr_val)

    result = pd.DataFrame(values, columns=cols)

    return result


def train_garch(dataframe: pd.DataFrame, column: str, lagtime: int) -> Tuple[float, float]:
    seed(1)
    data = (dataframe[column]).to_list()
    var = ((dataframe[column] ** 2)).to_list()
    n_test = 10

    train, test = data[:-n_test], data[-n_test:]
    model = arch_model(train, mean="Zero", vol="GARCH", p=lagtime, q=lagtime,  rescale=True)
    model_fit = model.fit()
    

    y_hat = model_fit.forecast(horizon=n_test, reindex=False)

    return (var[-n_test:], y_hat.variance.values[-1, :])










