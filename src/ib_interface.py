from datetime import datetime
import threading
import time

import numpy as np

from ibapi.wrapper import EWrapper
from ibapi.client import EClient

import log

"""
This module will handle the IBAccount class ; the interface between the
application and the broker (interactive broker)
"""


class IBApi(EWrapper, EClient):
    """
    A class used as an interface between the bot and the broker
    (interactive broker)

    ...

    Attributes
    ----------
    nextOrderId : int
        This attribute stores a valid orderId. Everytime the program needs
        an orderId, it will use the value of nextOrderId and increment the
        attribute by one.

    nextReqId : int
        Used to store a valid requestId. Needs to be incremented after each
        use.

    active_data_reqs : int
        Keeps track of the number of active market data requests. If it's
        value = 0, there is no market data being send by interactive brokers.

    reqId_info : dict
        Stores the symbol and the barsize of a market data request Id.

    orders : dict
        Large dictionnary that stores data about every order (the data returned
        by the openOrder, orderStatus, execDetails and commissionReport
        callbacks).

        It's a large dictionnary with a key for every order (the key = the
        orderId of the order). Every key has as value another dictionnary
        with data about the order.

    account : dict
        Another large dictionnary that stores data about the account (Data send
        by tws through the updateAccountValue callback)

    Methods (internal)
    -------

    """

    # variables and program
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = 0
        self.nextReqId = 0
        self.active_data_reqs = 0
        self.reqId_info = {}
        self.market = {}
        self.orders = {}
        self.account = {
            "AccountCode": np.nan,
            "AccountOrGroup": np.nan,
            "AccountReady": np.nan,
            "AccountType": np.nan,
            "AccruedCash": np.nan,
            "AccruedCash-C": np.nan,
            "AccruedCash-S": np.nan,
            "AccruedDividend": np.nan,
            "AccruedDividend-C": np.nan,
            "AccruedDividend-S": np.nan,
            "AvailableFunds": np.nan,
            "AvailableFunds-C": np.nan,
            "AvailableFunds-S": np.nan,
            "Billable": np.nan,
            "Billable-C": np.nan,
            "Billable-S": np.nan,
            "BuyingPower": np.nan,
            "CashBalance": np.nan,
            "CorporateBondValue": np.nan,
            "Currency": np.nan,
            "Cushion": np.nan,
            "DayTradesRemaining": np.nan,
            "DayTradesRemainingT+1": np.nan,
            "DayTradesRemainingT+2": np.nan,
            "DayTradesRemainingT+3": np.nan,
            "DayTradesRemainingT+4": np.nan,
            "EquityWithLoanValue": np.nan,
            "EquityWithLoanValue-C": np.nan,
            "EquityWithLoanValue-S": np.nan,
            "ExcessLiquidity": np.nan,
            "ExcessLiquidity-C": np.nan,
            "ExcessLiquidity-S": np.nan,
            "ExchangeRate": np.nan,
            "FullAvailableFunds": np.nan,
            "FullAvailableFunds-C": np.nan,
            "FullAvailableFunds-S": np.nan,
            "FullExcessLiquidity": np.nan,
            "FullExcessLiquidity-C": np.nan,
            "FullExcessLiquidity-S": np.nan,
            "FullInitMarginReq": np.nan,
            "FullInitMarginReq-C": np.nan,
            "FullInitMarginReq-S": np.nan,
            "FullMaintMarginReq": np.nan,
            "FullMaintMarginReq-C": np.nan,
            "FullMaintMarginReq-S": np.nan,
            "FundValue": np.nan,
            "FutureOptionValue": np.nan,
            "FuturesPNL": np.nan,
            "FxCashBalance": np.nan,
            "GrossPositionValue": np.nan,
            "GrossPositionValue-S": np.nan,
            "IndianStockHaircut": np.nan,
            "InitMarginReq": np.nan,
            "InitMarginReq-C": np.nan,
            "InitMarginReq-S": np.nan,
            "IssuerOptionValue": np.nan,
            "Leverage-S": np.nan,
            "LookAheadNextChange": np.nan,
            "LookAheadAvailableFunds": np.nan,
            "LookAheadAvailableFunds-C": np.nan,
            "LookAheadAvailableFunds-S": np.nan,
            "LookAheadExcessLiquidity": np.nan,
            "LookAheadExcessLiquidity-C": np.nan,
            "LookAheadExcessLiquidity-S": np.nan,
            "LookAheadInitMarginReq": np.nan,
            "LookAheadInitMarginReq-C": np.nan,
            "LookAheadInitMarginReq-S": np.nan,
            "LookAheadMaintMarginReq": np.nan,
            "LookAheadMaintMarginReq-C": np.nan,
            "LookAheadMaintMarginReq-S": np.nan,
            "MaintMarginReq": np.nan,
            "MaintMarginReq-C": np.nan,
            "MaintMarginReq-S": np.nan,
            "MoneyMarketFundValue": np.nan,
            "MutualFundValue": np.nan,
            "NetDividend": np.nan,
            "NetLiquidation": np.nan,
            "NetLiquidation-C": np.nan,
            "NetLiquidation-S": np.nan,
            "NetLiquidationByCurrency": np.nan,
            "OptionMarketValue": np.nan,
            "PASharesValue": np.nan,
            "PASharesValue-C": np.nan,
            "PASharesValue-S": np.nan,
            "PostExpirationExcess": np.nan,
            "PostExpirationExcess-C": np.nan,
            "PostExpirationExcess-S": np.nan,
            "PostExpirationMargin": np.nan,
            "PostExpirationMargin-C": np.nan,
            "PostExpirationMargin-S": np.nan,
            "PreviousDayEquityWithLoanValue": np.nan,
            "PreviousDayEquityWithLoanValue-S": np.nan,
            "RealCurrency": np.nan,
            "RealizedPnL": np.nan,
            "RegTEquity": np.nan,
            "RegTEquity-S": np.nan,
            "RegTMargin": np.nan,
            "RegTMargin-S": np.nan,
            "SMA": np.nan,
            "SMA-S": np.nan,
            "SegmentTitle": np.nan,
            "StockMarketValue": np.nan,
            "TBondValue": np.nan,
            "TBillValue": np.nan,
            "TotalCashBalance": np.nan,
            "TotalCashValue": np.nan,
            "TotalCashValue-C": np.nan,
            "TotalCashValue-S": np.nan,
            "TradingType-S": np.nan,
            "UnrealizedPnL": np.nan,
            "WarrantValue": np.nan,
            "WhatIfPMEnable": np.nan,
            "lastUpdate": np.nan,
            "startValue": np.nan,
            "TotalCashBalanceEvol": [], }
        self.portfolio = {}

    # external use

    # internal use
    def init_order(self, orderId):
        """
        creates a key in the order attribute for the order nb {{orderId}} so
        the program can add data for this orderId.

        Args:
            orderId (int): the orderId of the order.
        """
        self.orders[orderId] = {
            "contract": None,
            "order": None,
            "orderStatus": None,
            "orderId": None,
            "status": None,
            "filled": None,
            "remaining": None,
            "avgFillPrice": None,
            "permId": None,
            "parentId": None,
            "lastFillPrice": None,
            "clientId": None,
            "whyHeld": None,
            "mktCapPrice": None,
            "execution": None,
            "commissionReport": None,
        }

    def placeOrder(self, orderId, contract, order):
        """
        Places an order. official documentation :
        https://interactivebrokers.github.io/tws-api/order_submission.html#submission
        """
        super().placeOrder(orderId, contract, order)
        self.init_order(orderId)

    def reqHistoricalData(self, reqId, contract, endDateTime, durationStr,
                          barSizeSetting, whatToShow, useRTH, formatDate,
                          keepUpToDate, chartOptions):
        super().reqHistoricalData(reqId, contract, endDateTime, durationStr,
                                  barSizeSetting, whatToShow, useRTH,
                                  formatDate, keepUpToDate, chartOptions)
        self.market[reqId] = []
        self.active_data_reqs += 1

    # EWrapper callbacks documentation: https://interactivebrokers.github.io/tws-api
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextOrderId = orderId
        log.log(f"received new order id: {self.nextOrderId}")

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        log.log(f"received openOrder of order {orderId}")
        self.orders[orderId]["contract"] = contract
        self.orders[orderId]["order"] = order
        self.orders[orderId]["orderState"] = orderState

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                    permId, parentId, lastFillPrice, clientId, whyHeld,
                    mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice,
                            permId, parentId, lastFillPrice, clientId, whyHeld,
                            mktCapPrice)
        log.log(f"received orderStatus of order {orderId}")
        self.orders[orderId]["status"] = status
        self.orders[orderId]["filled"] = filled
        self.orders[orderId]["remaining"] = remaining
        self.orders[orderId]["avgFillPrice"] = avgFillPrice
        self.orders[orderId]["permId"] = permId
        self.orders[orderId]["parentId"] = parentId
        self.orders[orderId]["lastFillPrice"] = lastFillPrice
        self.orders[orderId]["clientId"] = clientId
        self.orders[orderId]["whyHeld"] = whyHeld
        self.orders[orderId]["mktCapPrice"] = mktCapPrice

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        log.log(f"received execDetails of order {execution.orderId}")
        self.orders[execution.orderId]["execution"] = execution

    def commissionReport(self, commissionReport):
        super().commissionReport(commissionReport)
        found = False
        for orderId in self.orders:
            if self.orders[orderId]["execution"].execId == commissionReport.execId:
                self.orders[orderId]["commissionReport"] = commissionReport
                log.log(f"received commission report for order {orderId}")
                found = True
        if not found:
            log.log("received commission report but couldn't find for which order")

    def updateAccountValue(self, key, val, currency, accountName):
        super().updateAccountValue(key, val, currency, accountName)
        self.account[key] = (val, currency)
        if key == "TotalCashBalance":
            value = (time.time(), val)
            self.account["TotalCashBalanceEvol"].append(value)
            if self.account["startValue"] == None:
                self.account["startValue"] = self.account["TotalCashBalance"]

    def updatePortfolio(self, contract, position, marketPrice, marketValue,
                        averageCost, unrealizedPNL, realizedPNL, accountName):
        symbol = f"{contract.secType}/{contract.currency}"
        self.portfolio[symbol] = {
            "contract": contract,
            "position": position,
            "marketPrice": marketPrice,
            "marketValue": marketValue,
            "averageCost": averageCost,
            "unrealizedPNL": unrealizedPNL,
            "realizedPNL": realizedPNL,
            "accountName": accountName}

    def updateAccountTime(self, timeStamp):
        super().updateAccountTime(timeStamp)
        self.account["last_update"] = timeStamp

    def accountDownloadEnd(self, accountName: str):
        super().accountDownloadEnd(accountName)
        log.log("updated account portfolio data")

    def error(self, id, errorCode, errorMsg):
        super().error(id, errorCode, errorMsg)
        log.log(f"{errorCode} {errorMsg}", level="ERROR")

    def historicalData(self, reqId, bar):
        if len(bar.date) == 8:
            dt = datetime.strptime(bar.date, r"%Y%m%d")

        else:
            dt = datetime.strptime(bar.date, r"%Y%m%d %H:%M:%S")

        timestamp = dt.timestamp()
        new_data = [timestamp, bar.open, bar.high, bar.low, bar.close]
        self.market[reqId].append(new_data)

    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        self.active_data_reqs -= 1

    def historicalDataUpdate(self, reqId, bar):
        if len(bar.date) == 8:
            dt = datetime.strptime(bar.date, r"%Y%m%d")

        else:
            dt = datetime.strptime(bar.date, r"%Y%m%d %H:%M:%S")

        timestamp = dt.timestamp()
        new_data = [timestamp, bar.open, bar.high, bar.low, bar.close]
        i_replace = [i for i, r in enumerate(
            self.market[reqId]) if r[0] == timestamp]
        for i in i_replace:
            del self.market[reqId][i]
        self.market[reqId].append(new_data)
