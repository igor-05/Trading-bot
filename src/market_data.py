import time

import numpy as np
import animation

from settings import get_settings
from contract import get_contract
from log import log

# variables:
data_type, symbols, timeframes = get_settings(
    "data_type", "symbols", "timeframes")


# external use :
def ask_data(ib):
    """Asks market data to interactive brokers for the symbols specified in
    settings. For each of those symbols, the function asks data in the
    specified barsizes and for the specified duration.

    Args:
        ib (IBApi obj): an IBApi object from which the data must be requested.
    """
    for symbol in symbols:
        reqIds = []
        contract = get_contract(symbol)
        log(f"asking data for {symbol}")
        start_time = time.time()
        for i in timeframes:
            barsize, duration = i
            reqId = ib.nextReqId
            reqIds.append(reqId)
            add_reqId_info(ib, reqId, symbol, barsize)
            ib.nextReqId += 1
            ib.reqHistoricalData(reqId, contract, "", duration,
                                 barsize, data_type, 0, 1, 0, [])
        log(f"waiting for {symbol} data")
        wait = animation.Wait()
        wait.start()
    while True:
        if ib.active_data_reqs == 0:
            wait.stop()
            log(f"all data for {symbol} has been retrieved")
            break

        if (start_time - time.time()) > 120:
            wait.stop()
            log("No data after 120 secs, cancelling requests." +
                " Program might have requested too much data.")
            for reqId in reqIds:
                ib.cancelHistoricalData(reqId)
            break


def get_data(ib, symbol, barsize=None, nb_of_data_points=0):
    """Returns market data of a specific symbol and barsize.

    Args:
        ib (IBApi obj): The IBApi object storing the data. 
        symbol (str): The security's symbol (i.e "EUR/USD") 
        barsize ([type]): The barsize (i.e "5 min", "4 hours", "1 hour").
        Defaults to None which means all the barsizes. 
        nb_of_data_points (int, optional): The number of bars to return.
        Defaults to 0 which means all the bars.

    Returns:
        numpy array: The data -> array([[timestamp, open, high, low, close],
                                        [timestamp, open, high, low, close],
                                        ...
                                        [timestamp, open, high, low, close]])
    """
    if barsize == None:
        barsizes = [tf[0] for tf in timeframes]
        data = []
        for barsize in barsizes:
            reqId = get_reqId_from_info(ib, symbol, barsize)
            if reqId == None:
                log(f"couldn't find data for {symbol} {barsize}")
                break
            bs_data = ib.market[reqId][-nb_of_data_points:]
            bs_data = np.array(bs_data, dtype=np.float64)
            bs_data = filter_arr(bs_data)
            data.append(bs_data)

    else:
        reqId = get_reqId_from_info(ib, symbol, barsize)
        if reqId == None:
            log(f"couldn't find data for {symbol} {barsize}")
        data = ib.market[reqId][-nb_of_data_points:]
        data = np.array(data, dtype=np.float64)
        data = filter_arr(data)

    return data


def get_dataframe():
    pass


def get_info_from_reqId(ib, reqId):
    return ib.reqId_info[reqId]


def get_reqId_from_info(ib, symbol, barsize):
    info = (symbol, barsize)
    for key in ib.reqId_info:
        if ib.reqId_info[key] == info:
            return key

    log(f"couldn't find any reqId for {barsize} {symbol}")
    return None


# internal use :
def add_reqId_info(ib, reqId, symbol, barsize):
    ib.reqId_info[reqId] = (symbol, barsize)


def filter_arr(arr):
    arr = arr[arr[:, 0].argsort()]
    _, unique_indices = np.unique(arr, return_index=True, axis=0)
    arr = arr[unique_indices]
    arr = arr[arr[:, 0] != -1]
    return arr


def req_ib_data(symbol):
    pass


def req_alphavantage_data(symbol):
    pass


# program :
