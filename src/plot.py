from datetime import datetime

import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np


import market_data
import indicators
from data import market_data as test_data

# variables :


# external use :
def plot_mkt_data(data, title=""):
    fig = mkt_data_fig(data)
    fig.update_layout(title_text=title)
    fig.show()


def plot_strategy_results(results):
    pass


def plot_rsi(data):
    rsi_data = indicators.rsi(data)
    rsi_data = np.array(rsi_data, dtype="object")
    for i in range(len(rsi_data)):
        rsi_data[i, 0] = datetime.fromtimestamp(rsi_data[i, 0])
    plt.figure(figsize=(15, 5))
    plt.title('RSI chart')
    plt.plot(rsi_data[:, 0], rsi_data[:, 1])

    plt.axhline(0, linestyle='--', alpha=0.1)
    plt.axhline(20, linestyle='--', alpha=0.5)
    plt.axhline(30, linestyle='--')

    plt.axhline(70, linestyle='--')
    plt.axhline(80, linestyle='--', alpha=0.5)
    plt.axhline(100, linestyle='--', alpha=0.1)
    plt.show()


def plot_sup_dem_zones(data, maximas, minimas):
    fig = mkt_data_fig(data)
    for i in maximas:
        dt = datetime.fromtimestamp(i[0])
        fig.add_hrect(y0=i[1], y1=i[2], line_width=0,
                      fillcolor="grey", opacity=0.2)

    for i in minimas:
        dt = datetime.fromtimestamp(i[0])
        fig.add_hrect(y0=i[1], y1=i[2], line_width=0,
                      fillcolor="grey", opacity=0.2)
    fig.show()


def plot_bollinger(data):
    b_data = indicators.bbands(data)
    b_data = np.array(b_data, dtype="object")
    for i in range(len(b_data)):
        b_data[i, 0] = datetime.fromtimestamp(b_data[i, 0])
    plt.figure(figsize=(15, 5))
    plt.plot(b_data[:, 0], b_data[:, 1])
    plt.plot(b_data[:, 0], b_data[:, 2])
    plt.plot(b_data[:, 0], b_data[:, 3])
    plt.show()


# internal use :
def mkt_data_fig(data):
    data = market_data.np_array_to_pd_df(data)
    fig = go.Figure(
        go.Candlestick(x=data["date"], open=data["open"],
                       high=data["high"], low=data["low"],
                       close=data["close"]))
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(yaxis_title="Price", xaxis_title="Date")
    return fig


# program :
if __name__ == "__main__":
    plot_mkt_data(test_data, title="Apple Stock")
