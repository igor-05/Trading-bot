from datetime import datetime

import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np


from market_data import np_array_to_pd_df
from indicators import rsi
from data import market_data

# variables :


# external use :
def plot_mkt_data(data, title=""):
    fig = mkt_data_fig(data)
    fig.update_layout(title_text=title)
    fig.show()


def plot_strategy_results(results):
    pass


def plot_rsi(data):
    rsi_data = rsi(data)
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

# internal use :


def mkt_data_fig(data):
    data = np_array_to_pd_df(data)
    fig = go.Figure(
        go.Candlestick(x=data["date"], open=data["open"],
                       high=data["high"], low=data["low"],
                       close=data["close"]))
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(yaxis_title="Price", xaxis_title="Date")
    return fig


# program :
if __name__ == "__main__":
    plot_mkt_data(market_data, title="Apple Stock")