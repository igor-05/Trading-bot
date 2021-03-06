from ibapi.contract import Contract

# variables :


# external use :
def get_contract(symbol):
    """returns a forex contract corresponding to the requested symbol.

    Args:
        symbol (str): The requested symbol.

    Returns:
        Contract obj: The returned Contract object.
    """
    contract = Contract()
    contract.symbol = symbol[:3]
    contract.secType = "CASH"  # get_settings("contract_security_type")
    contract.currency = symbol[4:]
    contract.exchange = "IDEALPRO"  # get_settings("contract_exchange")
    return contract

# internal use :

# program :
