import time
from datetime import datetime

import numpy as np
import pandas as pd
import animation

import settings
import contract
import log
import ib_interface
import session

# variables:
data_type = settings.get_settings("data_type")


# external use :
def clear_data(ib):
    log.log("purging outdated market data")
    reqs = [i for i in ib.market]
    ib.market = {}
    ib.reqId_info = {}
    for i in reqs:
        ib.cancelHistoricalData(i)


def ask_data(ib, symbols, timeframes):
    clear_data(ib)
    for symbol in symbols:
        reqIds = []
        symbol_contract = contract.get_contract(symbol)
        log.log(f"asking data for {symbol}")
        start_time = time.time()
        for i in timeframes:
            barsize, duration = i
            reqId = ib.nextReqId
            add_reqId_info(ib, reqId, symbol, barsize)
            ib.nextReqId += 1
            reqIds.append(reqId)
            ib.reqHistoricalData(reqId, symbol_contract, "", duration,
                                 barsize, data_type, 0, 1, 0, [])
        log.log(f"waiting for {symbol} data")
        wait = animation.Wait()
        wait.start()
        while True:
            if ib.active_data_reqs == 0:
                wait.stop()
                log.log(f"all data for {symbol} has been retrieved")
                break

            if (start_time - time.time()) > 120:
                wait.stop()
                log.log("No data after 120 secs, cancelling requests." +
                        " Program might have requested too much data.")
                for reqId in reqIds:
                    ib.cancelHistoricalData(reqId)
                break


def get_data(ib, symbol, barsize=None, nb_of_data_points=0, data_format="numpy"):
    """Returns market data of a specific symbol and barsize.

    Args:
        ib (IBApi obj): The IBApi object storing the data. 
        symbol (str): The security's symbol (i.e "EUR/USD") 
        barsize ([type]): The barsize (i.e "5 min", "4 hours", "1 hour").
        Defaults to None which means all the barsizes. 
        nb_of_data_points (int, optional): The number of bars to return.
        format (str, optional): The format. Either "numpy" for (np.array) or 
        "pandas" for a pandas.DataFrame
        Defaults to 0 which means all the bars.

    Returns:
        numpy array: The data -> array([[timestamp, open, high, low, close],
                                        [timestamp, open, high, low, close],
                                        ...
                                        [timestamp, open, high, low, close]])
    """
    if type(barsize) in (type(()), type([])):
        data = []
        barsizes = barsize.copy()
        del barsize
        for barsize in barsizes:
            reqId = get_reqId_from_info(ib, symbol, barsize)
            if reqId == None:
                log.log(f"couldn't find data for {symbol} {barsize}")
                break
            bs_data = ib.market[reqId][-nb_of_data_points:]
            bs_data = np.array(bs_data, dtype=np.float64)
            bs_data = filter_arr(bs_data)
            data.append(bs_data)
    else:
        reqId = get_reqId_from_info(ib, symbol, barsize)
        if reqId == None:
            log.log(f"couldn't find data for {symbol} {barsize}")
        data = ib.market[reqId][-nb_of_data_points:]
        data = np.array(data, dtype=np.float64)
        data = filter_arr(data)
    return data


def get_info_from_reqId(ib, reqId):
    return ib.reqId_info[reqId]


def get_reqId_from_info(ib, symbol, barsize):
    info = (symbol, barsize)
    for key in ib.reqId_info:
        if ib.reqId_info[key] == info:
            return key

    return None


def np_array_to_pd_df(arr):
    arr = np.array(arr, dtype='object')
    for i in range(len(arr)):
        arr[i][0] = datetime.fromtimestamp(arr[i][0])
    df = pd.DataFrame(arr, columns=["date", "open", "high", "low", "close"])
    return df


# internal use :
def add_reqId_info(ib, reqId, symbol, barsize):
    ib.reqId_info[reqId] = (symbol, barsize)


def filter_arr(arr):
    arr = arr[arr[:, 0].argsort()]
    _, unique_indices = np.unique(arr, return_index=True, axis=0)
    arr = arr[unique_indices]
    arr = arr[arr[:, 0] != -1]
    return arr


# program :
if __name__ == "__main__":
    ib = ib_interface.IBApi()
    session.start_session(ib)
    pairs = ["EUR/USD", "GBP/AUD", "GBP/USD", "GBP/JPY", "GBP/CAD", "USD/JPY"]
    tfs = [("1 min", "2 D"), ("5 mins", "1 W"),
           ("4 hours", "6 M"), ("1 day", "1 Y")]
    ask_data(ib, pairs, tfs,)
