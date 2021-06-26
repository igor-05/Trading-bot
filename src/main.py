from datetime import datetime
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


from ib_interface import IBApi
from market_data import get_data, ask_data, np_array_to_pd_df
from indicators import rsi, ema, macd, maximas_and_minimas
from plot import plot_rsi

"""the main program, currently used for testing"""


def main():
    ib = IBApi()
    ib.connect()
    time.sleep(2)
    ask_data(ib)
    data = get_data(ib, "EUR/USD", barsize="4 hours")
    a = time.time()
    maximas, minimas = maximas_and_minimas(data, 5)
    p(minimas)
    p(maximas)
    print("-"*50)
    # out = np.array(out, dtype="object")
    # for i in out:
    #     i[0] = datetime.fromtimestamp(i[0])
    # plt.plot(out[:, 0], out[:, 1])
    # plt.plot(out[:, 0], out[:, 2])
    # plt.show()
    # print("i")


def p(data):
    for i in data:
        print(datetime.fromtimestamp(i[0]), i[1])


if __name__ == '__main__':
    main()
