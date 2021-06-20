from datetime import datetime
import os
import os.path

from settings import get_settings

"""This module will handle everything log related """

# variables
log_file_path, print_log = get_settings("log_file_path", "print_logs")


# external


def log(msg, print_l=None):
    """
    logs a msg to the log file

    Args:
        msg (str): the message to log
        print_log (bool, optional): whether to print or not the logs to the
        terminal. If no value is specified, it will take the value of the
        print_log setting. Defaults to None.
    """
    if print_l == None:
        print_l = print_log

    log_msg = f"{datetime.now()} : {msg}"
    with open(log_file_path, "a") as f:
        f.write(f"{log_msg}\n")

    if print_l:
        print(log_msg)


# internal
def init_log_file():
    """Ensures there is a log file. If not, will create one"""
    if not os.path.exists(log_file_path):
        dirname = os.path.dirname(log_file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(log_file_path, "w") as f:
            f.write(f"{datetime.now()} : creating log file\n")


# program
init_log_file()
