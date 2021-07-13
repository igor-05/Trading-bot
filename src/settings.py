import os
import os.path
import json

"""This module will handle everything setting related """

# variables
path = r".settings.json"
default_settings = {
    "log_file_path": "logs.txt",
    "print_logs": True,
    "paper_trading": True,
    "data_type": "BID",
    "symbols": ["EUR/USD", ],
    "timeframes": [("1 min", "1 W"),
                   ("5 mins", "2 M"),
                   ("15 mins", "2 M"),
                   ("1 hour", "2 M"),
                   ("4 hours", "6 M"),
                   ("1 day", "2 Y")],

    "freecurrencyapi_key": "",  # get one at https://freecurrencyapi.net/

}


# external use
def get_all_settings():
    """returns all the settings and their values

    Returns:
        dict: a dictionnary describing the user settings.
    """
    with open(path, "r") as f:
        settings = json.load(f)
    return settings


def get_settings(*keys):
    """
    returns the values of specific settings.

    Args:
        keys (str): the name of the settings.

    Returns:
        * or list: the values of the settings. If multiple settings are asked,
        it returns a list with every value in order.
    """
    settings = get_all_settings()
    if len(keys) > 1:
        values = []
        for key in keys:
            values.append(settings[key])
        return values
    else:
        return settings[keys[0]]


def update_settings(key, value):
    """
    updates a setting.

    Args:
        key (string): the name of the setting.
        value (*): the new value of the specified setting.
    """
    settings = get_all_settings()
    settings[key] = value
    dump_settings(settings)


# internal use
def init_settings():
    """
    Ensures there is a settings file. If not, will create one with default
    settings.
    """
    if not os.path.exists(path):
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(path, "w") as f:
            json.dump(default_settings, f)


def dump_settings(settings):
    """
    overrides the settings with new settings.

    Args:
        settings (dict): the new settings
    """
    with open(path, "w") as f:
        json.dump(settings, f)


# program
init_settings()
