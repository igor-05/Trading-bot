import requests
import json
import cachetools.func

from ibapi.order import Order

import log
import settings
import contract

# variables
currency_rates_api_key = settings.get_settings("freecurrencyapi_key")

# external use :


def bracket_order(ib, symbol, action, stp_price, lmt_price, size):
    """Places a forex order

    Args:
        ib ([type]): [description]
        symbol ([type]): [description]
        action ([type]): [description]
        stp_price ([type]): [description]
        lmt_price ([type]): [description]
        size ([type]): [description]
    """
    symbol_contract = contract.get_contract(symbol)
    size_in_base_currency = usd_to_currency(size, symbol_contract.currency)

    parent = Order()
    parent.orderId = ib.nextOrderId
    ib.nextOrderId += 1
    parent.action = action
    parent.orderType = "MKT"
    parent.cashQty = size_in_base_currency

    take_profit = Order()
    take_profit.orderId = ib.nextOrderId
    ib.nextOrderId += 1
    take_profit.action = "SELL" if action == "BUY" else "BUY"
    take_profit.lmtPrice = lmt_price
    take_profit.cashQty = size_in_base_currency
    take_profit.parentId = parent.orderId
    take_profit.transmit = False

    stop_loss = Order()
    stop_loss.orderId = ib.nextOrderId
    ib.nextOrderId += 1
    stop_loss.action = "SELL" if action == "BUY" else "BUY"
    stop_loss.orderType = "STP"
    stop_loss.auxPrice = stp_price
    stop_loss.cashQty = size_in_base_currency
    stop_loss.parentId = parent.orderId
    stop_loss.transmit = True

    bracket_order = [parent, take_profit, stop_loss]
    for order in bracket_order:
        ib.placeOrder(order.orderId, symbol_contract, order)
        log.log(f"placing order {order.orderId}")


def option_order():
    pass


# internal use :
@cachetools.func.ttl_cache(ttl=10 * 60)
def get_usd_rates():
    url = "https://freecurrencyapi.net/api/v1/rates?base_currency=USD"
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'apikey': currency_rates_api_key}
    response = requests.get(url, headers=headers)
    if not response.ok:
        log.log("couldn't connect to currency rate api")
    rates = json.loads(response.text)["data"]
    rates = rates[list(rates.keys())[0]]
    return rates


def usd_to_currency(usd_value, to_currency):
    rates = get_usd_rates()

    try:
        usd_to_currency_rate = rates[to_currency]
        return usd_value * usd_to_currency_rate
    except KeyError():
        log.log(
            f"asked currency rate for {to_currency}/USD but it doesn't exist")


# program :
if __name__ == "__main__":
    print(usd_to_currency(500, "EUR"))
    print(usd_to_currency(500, "GBP"))
