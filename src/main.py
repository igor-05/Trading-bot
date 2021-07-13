from datetime import datetime
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


"""the main program, currently used for testing"""


def main():
    pass


def p(data):
    for i in data:
        print(datetime.fromtimestamp(i[0]), i[1])


if __name__ == '__main__':
    main()
