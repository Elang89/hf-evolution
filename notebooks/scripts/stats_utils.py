import pandas as pd
import math

from scipy.stats import describe

import statsmodels.api as sm
import numpy as np

from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import het_white, het_arch
from typing import Callable, Dict, Tuple
from arch import arch_model
from random import seed, sample
from collections import Counter
from scipy.stats import mannwhitneyu
from scipy import stats as st

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

def stat_test(
        dataframe1: pd. DataFrame, 
        dataframe2: pd.DataFrame, 
        fn: Callable[[pd.DataFrame, pd.DataFrame], pd.DataFrame]
    ) -> pd.DataFrame:

    names = []
    t_stats = []
    p_values = []
    
    for column in dataframe1:

        vector_1 = dataframe1[column].to_list()
        vector_2 = dataframe2[column].to_list()

        sample_size_1 = calculate_sample_size(0.95, 0.05, len(vector_1))
        sample_size_2 = calculate_sample_size(0.95, 0.05, len(vector_2))

        vector_1 = sample(vector_1, sample_size_1)
        vector_2 = sample(vector_2, sample_size_2)

        result = fn(vector_1, vector_2)
        t_stat = result.statistic
        p_value = result.pvalue

        names.append(column)
        t_stats.append(t_stat)
        p_values.append(p_value)

    return pd.DataFrame({"Distribution": names, "t-statistic": t_stats, "p-value": p_values})

def white_normal(dataframe: pd.DataFrame) -> pd.DataFrame:
    distributions = []
    t_stats = []
    p_values = []
    f_stats = []
    fp_values = []

    for column in dataframe: 
        current_vector = dataframe[column].to_list()
        counter = Counter(current_vector)
        x = list(counter.keys())
        y = list(counter.values())
        y = sm.add_constant(y)

        model = sm.OLS(x, y).fit()
        t_stat, p_value, f_stat, fp_value = het_white(model.resid, model.model.exog)

        distributions.append(column)
        t_stats.append(t_stat)
        p_values.append(p_value)
        f_stats.append(f_stat)
        fp_values.append(fp_value)

    return pd.DataFrame({
        "Distribution": distributions,
        "White t-statistic": t_stats,
        "White p-value": p_values,
        "White f-statistic": f_stats,
        "White fp value": fp_values
    })


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


def calculate_sample_size(
    c_level: float,
    c_interval: float, 
    population_size: int,
    proportion: float = 0.5,
) -> int:
    auc = (1 + c_level) / 2

    z_score = st.norm.ppf(auc)
    X = (z_score/c_interval)**2 * (proportion)*(1 - proportion)

    result = int((population_size * X) / (X + population_size - 1))

    return result










