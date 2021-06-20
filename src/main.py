# currently used for testing.
from datetime import datetime
import time


from ib_interface import IBApi
from market_data import get_data, ask_data
from indicators import rsi


def main():
    ib = IBApi()
    ib.connect()
    time.sleep(2)
    ask_data(ib)
    data = get_data(ib, "EUR/USD", barsize="1 min")
    print([list(i) for i in data])
    # for i in data:
    #     print(i)


def p(data):
    for i in data:
        print(datetime.fromtimestamp(i[0]), i[4])


if __name__ == '__main__':
    main()
