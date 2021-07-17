import warnings
import time
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from vectorized_ema import ewma_vectorized_safe as ewma
from data import market_data as test_data
import plot
import ib_interface
import session
import market_data

from finta import TA

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
def sma(data, window):
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
    ema = ewma(close_prices, alpha)
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

    out = np.zeros((data.shape[0], 4), dtype=np.float64)
    out[:, 0] = data[:, 0]  # timestamps

    # macd line :
    out[:, 1] = ewma(data[:, 4], fast_alpha) - ewma(data[:, 4], slow_alpha)
    out[:, 2] = ewma(out[:, 1], signal_alpha)  # signal line
    out[:, 3] = out[:, 1] - out[:, 2]  # histogram
    return out


def avg_volatility(data):
    deltas = np.absolute(data[:, 4] - data[:, 1])
    avg = np.sum(deltas) / deltas.shape[0]
    return avg


def bbands(data, period=20, std_multiplier=2):
    sigmas = std(data, period)
    out = np.zeros((data.shape[0], 4), np.float64)
    out[:, 0] = data[:, 0]  # timestamps
    out[:, 1] = sma(data, period)[:, 1]  # middle band
    out[:, 2] = out[:, 1] + sigmas[:, 1] * std_multiplier  # upper band
    out[:, 3] = out[:, 1] - sigmas[:, 1] * std_multiplier  # lower band
    return out


def adx(data, period=14):
    dmp = np.diff(data[:, 2])
    dmn = -np.diff(data[:, 3])
    dmp[np.logical_not(np.logical_and(dmp > 0, dmp > dmn))] = 0
    dmn[np.logical_not(np.logical_and(dmn > 0, dmn > dmp))] = 0

    tr = np.zeros((data.shape[0] - 1, 3), np.float64)
    tr[:, 0] = np.abs(data[1:, 2] - data[1:, 3])
    tr[:, 1] = np.abs(data[1:, 2] - data[:-1, 4])
    tr[:, 2] = np.abs(data[:-1, 4] - data[1:, 3])
    tr = np.amax(tr, axis=1)
    atr = moving_average(tr, period)

    alpha = 1 / period
    diplus = dmp[period-1:] / atr
    diplus = 100 * ewma(diplus, alpha)
    diminus = dmn[period-1:] / atr
    diminus = 100 * ewma(diminus, alpha)

    ADX = np.abs(diplus - diminus) / (diplus + diminus)
    ADX = 100 * ewma(ADX, alpha)

    out = np.full((data.shape[0], 4), np.nan, dtype=np.float64)
    out[:, 0] = data[:, 0]
    out[period:, 1] = ADX
    out[period:, 2] = diplus
    out[period:, 3] = diminus

    return out


# internal :
def moving_average(a, n):
    ret = np.cumsum(a)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def std(data, period):
    closing_prices = data[:, 4]
    windows = np.zeros((data.shape[0] - period, period), np.float64)
    for i in range(period):
        windows[:, i] = closing_prices[i:windows.shape[0]+i]
    std = np.std(windows, axis=1)
    extra_values = np.zeros(period)
    extra_values[:] = np.nan
    std = np.concatenate((extra_values, std))
    return np.stack((data[:, 0], std), axis=1)


# program
if __name__ == '__main__':
    ib = ib_interface.IBApi()
    session.start_session(ib)
    market_data.ask_data(ib, ["EUR/USD", ], [("1 hour", "3 M"), ])
    data = market_data.get_data(ib, "EUR/USD", barsize="1 hour")

    ADX = adx(data)
    dates = np.array(ADX[:, 0], dtype="object")
    for i in range(len(dates)):
        dates[i] = datetime.fromtimestamp(dates[i])
