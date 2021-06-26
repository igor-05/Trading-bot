import warnings
import time

import numpy as np
import pandas as pd

from vectorized_ema import ewma_vectorized_safe
from data import market_data as test_data

"""
Module storing functions returning technical indicators.

Rules for the function :
    - input = numpy array containing market data in format :
        np.ndarray([[timestamp, open, high, low, close],
                    [timestamp, open, high, low, close],
                    ...,
                    [timestamp, open, high, low, close]], dtype=np.float64)
            (format return by market_data.get_data)

    - output must be the same length as input ; for every inputted row,
        there must be a value in the output. To indicate no value, use np.nan.
        The format of the output is :
        np.ndarray([[timestamp, value1,...],
                    ...,
                    [timestamp, value1,...],])
"""


# external :
def ma(data, window):
    close_prices = data[:, 4]
    ma = moving_average(close_prices, window)

    # formating data :
    extra_values = np.zeros(window - 1)
    extra_values[:] = np.nan
    ma = np.concatenate((extra_values, ma))
    return np.stack((data[:, 0], ma), axis=1)


def ema(data, window):
    alpha = 2/(window + 1)
    close_prices = data[:, 4]
    ema = ewma_vectorized_safe(close_prices, alpha)
    return np.stack((data[:, 0], ema), axis=1)


def rsi(data, period=14):
    delta = np.diff(data[:, 4])

    positive = delta.copy()
    negative = delta.copy()

    positive[positive < 0] = 0
    negative[negative > 0] = 0

    average_gain = moving_average(positive, period)
    average_loss = moving_average(np.abs(negative), period)
    relative_strength = average_gain / average_loss
    RSI = 100 - (100 / (1 + relative_strength))

    # formating data :
    extra_values = np.zeros(period)
    extra_values[:] = np.nan
    RSI = np.concatenate((extra_values, RSI))
    return np.stack((data[:, 0], RSI), axis=1)


def macd(data, fast=12, slow=26, signal=9):
    fast_alpha = 2/(fast + 1)
    slow_alpha = 2/(slow + 1)
    signal_alpha = 2/(signal + 1)

    out = np.zeros((len(data), 4), dtype=np.float64)
    out[:, 0] = data[:, 0]

    # macd line :
    out[:, 1] = ewma_vectorized_safe(
        data[:, 4], fast_alpha) - ewma_vectorized_safe(data[:, 4], slow_alpha)
    # signal line :
    out[:, 2] = ewma_vectorized_safe(out[:, 1], signal_alpha)
    # histogram :
    out[:, 3] = out[:, 1] - out[:, 2]
    return out


def avg_volatility(data):
    deltas = data[:, 2] - data[:, 3]
    avg = np.sum(deltas) / deltas.shape[0]
    return avg


def sup_and_res(data):
    pass


# internal :
def moving_average(a, n):
    ret = np.cumsum(a)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def maximas_and_minimas(data, winsize, delta=None, smooth_prices=False):
    if delta == None:
        delta = avg_volatility(data) * winsize

    if smooth_prices:
        close_prices = ema(data, 20)
        if delta == None:
            delta = np.sum(
                np.abs(np.diff(close_prices[:, 1]))) / len(close_prices)
            delta = delta * winsize
    else:
        close_prices = data[:, (0, 4)]

    col_nb = 2 * winsize + 1
    windows = np.zeros((data.shape[0] - 2 * winsize, col_nb))
    for i in range(col_nb):
        windows[:, i] = close_prices[i:windows.shape[0]+i, 1]

    maximas = np.stack(
        (data[winsize:-winsize, 0], windows.max(axis=1)), axis=1)

    minimas = np.stack(
        (data[winsize:-winsize, 0], windows.min(axis=1)), axis=1)

    cond1 = np.array((maximas[:, 1] - windows[:, 0]) > delta, dtype=np.byte)
    cond2 = np.array((maximas[:, 1] - windows[:, -1]) > delta, dtype=np.byte)
    cond3 = np.array(maximas[:, 1] == windows[:, winsize], dtype=np.byte)
    maximas = maximas[cond1+cond2+cond3 == 3]

    cond1 = np.array((windows[:, 0] - minimas[:, 1]) > delta, dtype=np.byte)
    cond2 = np.array((windows[:, -1] - minimas[:, 1]) > delta, dtype=np.byte)
    cond3 = np.array(minimas[:, 1] == windows[:, winsize], dtype=np.byte)
    minimas = minimas[cond1+cond2+cond3 == 3]
    del windows, cond1, cond2, cond3
    return maximas, minimas


# program
warnings.filterwarnings("ignore", category=RuntimeWarning)
if __name__ == '__main__':
    a = ema(test_data, 20)
    print(a)
