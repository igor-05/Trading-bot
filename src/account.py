# variables :


# external use :
def get_account_data(ib, *keys):
    return get_lmt_dictionnary(ib.account, *keys)


def get_portfolio_data(ib, *symbols):
    return get_lmt_dictionnary(ib.portfolio, *symbols)


# internal use :
def get_lmt_dictionnary(dictionnary, *keys):
    if not keys:
        return dictionnary
    lmt_dictionnary = {}
    for key in keys:
        lmt_dictionnary[key] = dictionnary[key]
    return lmt_dictionnary

# program :
