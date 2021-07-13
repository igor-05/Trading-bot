import threading
import time

import settings
import log


def start_session(ib):
    """
    Opens a socket/connection between the IBAccount object and the
    broker
    """

    paper_trading = settings.get_settings("paper_trading")
    port = 7496 if not paper_trading else 7497

    log.log("connecting to the broker")
    ib.connect("127.0.0.1", port, 0)
    time.sleep(2)
    thread = threading.Thread(target=ib.run, daemon=True)
    thread.start()
    start_time = time.time()
    while True:
        if isinstance(ib.nextOrderId, int):
            log.log("connection successful")
            time.sleep(2)
            break
        if time.time() - start_time < 30:
            log.log("failed to connect", level="ERROR")
            return 0
    log.log("subscribing to account updates")
    ib.reqAccountUpdates(True, ib.account)
    return 1


def stop_session(ib):
    log.log("disconnecting from tws")
    ib.reqAccountUpdates(True, ib.account)
    ib.disconnect()


def start_bot(ib):
    pass


def stop_bot(ib):
    pass
