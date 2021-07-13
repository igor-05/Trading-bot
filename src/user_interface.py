from functools import partial
import threading

from tkinter import ttk
import tkinter as tk

import ib_interface
import log
import account
import session


def run_in_thread(fn):
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t  # <-- this is new!
    return run


class MainFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.widget_dict = {}

        self.portfolio_frame = self.get_portfolio_frame()
        self.account_frame = self.get_account_frame()
        self.control_frame = self.get_control_frame()

        self.account_frame.pack(fill="both", expand="yes", padx=20, pady=10)
        self.portfolio_frame.pack(fill="both", expand="yes", padx=20, pady=10)
        self.control_frame.pack(fill="both", expand="yes", padx=20, pady=10)

    def get_account_frame(self):
        frame = ttk.LabelFrame(self, text="Account")
        keys = ["TotalCashBalance", "CashBalance", "RealizedPnL",
                "UnrealizedPnL", "startValue"]
        lab_names = ["Account balance", "Available cash", "Realized profit",
                     "Unrealized profit", "Account start value"]
        data = list(account.get_account_data(self.parent.ib, *keys).values())
        for i in range(len(data)):
            lab = ttk.Label(frame, anchor="w", font=20)
            self.widget_dict[keys[i]] = lab
            if keys[i] in ["RealizedPnL", "UnrealizedPnL"]:
                text = f"{lab_names[i]} : {data[i]} " + \
                    f"({round((data[i]/data[-1])*100, 2)} %)"
                color = "red" if data[i] < 0 else "green"
                lab.config(text=text, foreground=color)
            else:
                text = f"{lab_names[i]} : {data[i]}"
                lab.config(text=text)
            lab.pack(fill="both", expand="yes")
        return frame

    def update_account(self):
        keys = ["TotalCashBalance", "CashBalance", "RealizedPnL",
                "UnrealizedPnL", "startValue"]
        lab_names = ["Account balance", "Available cash", "Realized profit",
                     "Unrealized profit", "Account start value"]
        data = list(account.get_account_data(self.parent.ib, *keys).values())
        for i in range(len(data)):
            lab = self.widget_dict[keys[i]]
            if keys[i] in ["RealizedPnL", "UnrealizedPnL"]:
                text = f"{lab_names[i]} : {data[i]} " + \
                    f"({round((data[i]/data[-1])*100, 2)} %)"
                color = "red" if data[i] < 0 else "green"
                lab.config(text=text, foreground=color)
            else:
                text = f"{lab_names[i]} : {data[i]}"
                lab.config(text=text)

    def get_portfolio_frame(self):
        frame = ttk.LabelFrame(self, text="Positions")
        tree = ttk.Treeview(frame, columns=(0, 1, 2, 3, 4, 5),
                            show="headings", height="6")
        self.widget_dict["tree"] = tree

        column_names = ["Symbol", "Positions", "Buying price",
                        "Current price", "Unrealized Profit", "Realized Profit"]
        i = 0
        for name in column_names:
            tree.heading(i, text=name)
            i += 1

        data = account.get_portfolio_data(self.parent.ib)
        for symbol in data:
            row = (symbol,
                   data[symbol]["position"],
                   data[symbol]["averageCost"],
                   data[symbol]["marketPrice"],
                   data[symbol]["unrealizedPNL"],
                   data[symbol]["realizedPNL"])
            tree.insert("", "end", values=row)
        tree.pack(side="left", fill="both")
        return frame

    def update_portfolio(self):
        tree = self.widget_dict["tree"]
        tree.delete(*tree.get_children())
        data = account.get_portfolio_data(self.parent.ib)
        for symbol in data:
            row = (symbol,
                   data[symbol]["position"],
                   data[symbol]["averageCost"],
                   data[symbol]["marketPrice"],
                   data[symbol]["unrealizedPNL"],
                   data[symbol]["realizedPNL"])
            tree.insert("", "end", values=row)

    def get_control_frame(self):
        frame = ttk.LabelFrame(self, text="Bot control")

        connect_button = tk.Button(frame)
        start_button = tk.Button(frame)
        self.widget_dict["connect_button"] = connect_button
        self.widget_dict["start_button"] = start_button

        connect_button.config(text="connect", anchor="s", foreground="green",
                              command=self.conn_butt_action)
        start_button.config(text="start",  anchor="s", foreground="green",
                            command=self.start_butt_action)

        connect_button.pack(side="right", padx=20, pady=5)
        start_button.pack(side="right", padx=20, pady=5)
        return frame

    @run_in_thread
    def conn_butt_action(self):
        connected = session.start_session(self.parent.ib)
        if connected:
            self.widget_dict["connect_button"].config(
                text="disconnect", command=self.disc_butt_action,
                foreground="red")
            self.parent.connected = True

    @run_in_thread
    def disc_butt_action(self):
        session.stop_session(self.parent.ib)
        self.widget_dict["connect_button"].config(
            text="connect", command=self.conn_butt_action, foreground="green")
        self.parent.connected = False

    def start_butt_action(self):
        if self.parent.connected:
            session.start_bot(self.parent.ib)
            self.widget_dict["start_button"].config(
                text="stop", command=self.stop_butt_action, foreground="red")
        else:
            log.log("can't start the bot because the application isn't" +
                    " connected to the broker")

    def stop_butt_action(self):
        session.stop_bot(self.parent.ib)
        self.widget_dict["start_button"].config(
            text="start", command=self.start_butt_action, foreground="green")

    def update(self):
        self.update_account()
        self.update_portfolio()


class App(tk.Tk):
    def __init__(self, ib):
        super().__init__()
        self.ib = ib
        self.active_window = "main"
        self.connected = False

        self.toolbar = self.get_toolbar()
        self.statusbar = self.get_status_bar()
        self.frame = None

        self.title("trading bot")
        self.minsize(1400, 900)
        self.maxsize(1400, 900)

        self.toolbar.pack(fill="x", side="top")
        self.fill_frame("home")
        self.statusbar.pack(side="bottom", fill="x")

        self.after(20, self.update)

    def get_toolbar(self):
        toolbar = ttk.Frame(self)
        button_names = ["home", "account", "orders", "market data",
                        "plots", "backtesting", "settings"]

        for name in button_names:
            button = ttk.Button(toolbar)
            button.config(text=name, command=partial(self.fill_frame, name))
            button.pack(side="left")
        return toolbar

    def get_status_bar(self):
        status = [x.strip() for x in log.get_last_log().split(":")[-2:]]
        statusbar = ttk.Label(self)
        color = "red" if status[0] == "ERROR" else "black"
        statusbar.config(text=status[1], borderwidth=2, relief="sunken",
                         anchor="w", foreground=color)
        return statusbar

    def fill_frame(self, frame_name):
        name_to_frame = {"home": MainFrame,
                         "account": None,
                         "orders": None,
                         "market data": None,
                         "plots": None,
                         "backtesting": None,
                         "settings": None}
        if self.frame:
            self.frame.pack_forget()
            self.frame.destroy()
        frame = name_to_frame[frame_name](self)
        frame.pack(expand="yes", fill="both")
        self.frame = frame

    def update(self):
        status = [x.strip() for x in log.get_last_log().split(":")[-2:]]
        color = "red" if status[0] == "ERROR" else "black"
        self.statusbar.config(text=status[1], foreground=color)
        self.frame.update()
        self.after(20, self.update)


# internal use


def doNothing():
    pass


if __name__ == "__main__":
    ib = ib_interface.IBApi()
    app = App(ib)
    app.mainloop()
