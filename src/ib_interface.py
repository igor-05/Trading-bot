from datetime import datetime
import threading
import time

from ibapi.wrapper import EWrapper
from ibapi.client import EClient

from log import log
from settings import get_settings
from stop_program import stop_program

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
            "AccountCode": None,
            "AccountOrGroup": None,
            "AccountReady": None,
            "AccountType": None,
            "AccruedCash": None,
            "AccruedCash-C": None,
            "AccruedCash-S": None,
            "AccruedDividend": None,
            "AccruedDividend-C": None,
            "AccruedDividend-S": None,
            "AvailableFunds": None,
            "AvailableFunds-C": None,
            "AvailableFunds-S": None,
            "Billable": None,
            "Billable-C": None,
            "Billable-S": None,
            "BuyingPower": None,
            "CashBalance": None,
            "CorporateBondValue": None,
            "Currency": None,
            "Cushion": None,
            "DayTradesRemaining": None,
            "DayTradesRemainingT+1": None,
            "DayTradesRemainingT+2": None,
            "DayTradesRemainingT+3": None,
            "DayTradesRemainingT+4": None,
            "EquityWithLoanValue": None,
            "EquityWithLoanValue-C": None,
            "EquityWithLoanValue-S": None,
            "ExcessLiquidity": None,
            "ExcessLiquidity-C": None,
            "ExcessLiquidity-S": None,
            "ExchangeRate": None,
            "FullAvailableFunds": None,
            "FullAvailableFunds-C": None,
            "FullAvailableFunds-S": None,
            "FullExcessLiquidity": None,
            "FullExcessLiquidity-C": None,
            "FullExcessLiquidity-S": None,
            "FullInitMarginReq": None,
            "FullInitMarginReq-C": None,
            "FullInitMarginReq-S": None,
            "FullMaintMarginReq": None,
            "FullMaintMarginReq-C": None,
            "FullMaintMarginReq-S": None,
            "FundValue": None,
            "FutureOptionValue": None,
            "FuturesPNL": None,
            "FxCashBalance": None,
            "GrossPositionValue": None,
            "GrossPositionValue-S": None,
            "IndianStockHaircut": None,
            "InitMarginReq": None,
            "InitMarginReq-C": None,
            "InitMarginReq-S": None,
            "IssuerOptionValue": None,
            "Leverage-S": None,
            "LookAheadNextChange": None,
            "LookAheadAvailableFunds": None,
            "LookAheadAvailableFunds-C": None,
            "LookAheadAvailableFunds-S": None,
            "LookAheadExcessLiquidity": None,
            "LookAheadExcessLiquidity-C": None,
            "LookAheadExcessLiquidity-S": None,
            "LookAheadInitMarginReq": None,
            "LookAheadInitMarginReq-C": None,
            "LookAheadInitMarginReq-S": None,
            "LookAheadMaintMarginReq": None,
            "LookAheadMaintMarginReq-C": None,
            "LookAheadMaintMarginReq-S": None,
            "MaintMarginReq": None,
            "MaintMarginReq-C": None,
            "MaintMarginReq-S": None,
            "MoneyMarketFundValue": None,
            "MutualFundValue": None,
            "NetDividend": None,
            "NetLiquidation": None,
            "NetLiquidation-C": None,
            "NetLiquidation-S": None,
            "NetLiquidationByCurrency": None,
            "OptionMarketValue": None,
            "PASharesValue": None,
            "PASharesValue-C": None,
            "PASharesValue-S": None,
            "PostExpirationExcess": None,
            "PostExpirationExcess-C": None,
            "PostExpirationExcess-S": None,
            "PostExpirationMargin": None,
            "PostExpirationMargin-C": None,
            "PostExpirationMargin-S": None,
            "PreviousDayEquityWithLoanValue": None,
            "PreviousDayEquityWithLoanValue-S": None,
            "RealCurrency": None,
            "RealizedPnL": None,
            "RegTEquity": None,
            "RegTEquity-S": None,
            "RegTMargin": None,
            "RegTMargin-S": None,
            "SMA": None,
            "SMA-S": None,
            "SegmentTitle": None,
            "StockMarketValue": None,
            "TBondValue": None,
            "TBillValue": None,
            "TotalCashBalance": None,
            "TotalCashValue": None,
            "TotalCashValue-C": None,
            "TotalCashValue-S": None,
            "TradingType-S": None,
            "UnrealizedPnL": None,
            "WarrantValue": None,
            "WhatIfPMEnable": None,
            "last_update": None,
        }

    # external use

    def connect(self):
        """
        Opens a socket/connection between the IBAccount object and the
        broker
        """

        paper_trading = get_settings("paper_trading")
        port = 7496 if not paper_trading else 7497

        log("connecting to the broker")
        super().connect("127.0.0.1", port, 0)
        time.sleep(2)
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        start_time = time.time()
        while True:
            if isinstance(self.nextOrderId, int):
                log("connection successful")
                break
            if time.time() - start_time < 30:
                log("failed to connect")
                stop_program()
                break

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
        log(f"received new order id: {self.nextOrderId}")

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        log(f"received openOrder of order {orderId}")
        self.orders[orderId]["contract"] = contract
        self.orders[orderId]["order"] = order
        self.orders[orderId]["orderState"] = orderState

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                    permId, parentId, lastFillPrice, clientId, whyHeld,
                    mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice,
                            permId, parentId, lastFillPrice, clientId, whyHeld,
                            mktCapPrice)
        log(f"received orderStatus of order {orderId}")
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
        log(f"received execDetails of order {execution.orderId}")
        self.orders[execution.orderId]["execution"] = execution

    def commissionReport(self, commissionReport):
        super().commissionReport(commissionReport)
        found = False
        for orderId in self.orders:
            if self.orders[orderId]["execution"].execId == commissionReport.execId:
                self.orders[orderId]["commissionReport"] = commissionReport
                log(f"received commission report for order {orderId}")
                found = True
        if not found:
            log("received commission report but couldn't find for which order")

    def updateAccountValue(self, key, val, currency, accountName):
        super().updateAccountValue(key, val, currency, accountName)
        self.account[key] = (val, currency)

    def updateAccountTime(self, timeStamp):
        super().updateAccountTime(timeStamp)
        self.account["last_update"] = timeStamp

    def accountDownloadEnd(self, accountName: str):
        super().accountDownloadEnd(accountName)
        log("updated account portfolio data")

    def error(self, id, errorCode, errorMsg):
        super().error(id, errorCode, errorMsg)
        if id != -1:
            log(f"ERROR : {errorCode} {errorMsg}", print_l=False)
            # stop_program()

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
