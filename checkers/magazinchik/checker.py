#!/usr/bin/env python3

import sys
import requests
import json
from checklib import *
import random
import string
import traceback

from checklib.checker import CheckFinished

PORT = 8080


class CheckMachine:
    @property
    def url(self):
        return f"http://{self.c.host}:{self.port}"

    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.port = PORT

    def register(self, session: requests.Session, username: str, password: str):
        url = f"{self.url}/register"
        data = {
            "username": username,
            "password": password,
        }
        response = session.post(url, data=data)

        self.c.assert_eq(response.status_code, 200, "Failed to register user")

        self.login(session, username, password, Status.MUMBLE)

    def login(
        self, session: requests.Session, username: str, password: str, status: Status
    ):
        url = f"{self.url}/login"
        data = {
            "username": username,
            "password": password,
        }
        response = session.post(url, data=data)

        self.c.assert_eq(response.status_code, 200, "Failed to login", status)

    def create_order(
        self, session: requests.Session, name: str, description: str, price: int
    ):
        url = f"{self.url}/order"
        data = {
            "name": name,
            "description": description,
            "price": price,
        }
        response = session.post(url, data=data)
        self.c.assert_eq(response.status_code, 302, "Failed to create order")

    def buy_order(self, session: requests.Session, product_id: str, status: Status):
        url = f"{self.url}/buy?product_id={product_id}"
        response = session.get(url)
        self.c.assert_eq(response.status_code, 200, "Failed to buy order", status)

    def get_order(self, session: requests.Session, status: Status) -> str:
        url = f"{self.url}/my_order"
        response = session.get(url)
        self.c.assert_eq(response.status_code, 200, "Failed to get orders", status)
        return response.text


def rnd_integer(min_value: int, max_value: int) -> int:
    return random.randint(min_value, max_value)


class Checker(BaseChecker):
    vulns: int = 2
    timeout: int = 15
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            self.cquit(
                Status.DOWN,
                "Connection error",
                f"Got requests connection error: {str(e)}",
            )

    def check(self):
        session = get_initialized_session()
        username, password = rnd_username(), rnd_password()

        order_name = rnd_string(9)
        order_description = rnd_string(20)
        order_price = rnd_integer(10, 50)

        self.mch.register(session, username, password)
        self.mch.login(session, username, password, Status.MUMBLE)
        self.mch.create_order(session, order_name, order_description, order_price)

        self.mch.buy_order(session, order_name, Status.MUMBLE)

        orders = self.mch.get_order(session, Status.MUMBLE)
        self.assert_in(order_name, orders, "Order not found in the list")
        self.assert_in(
            order_description, orders, "Order description not found in the list"
        )

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        username, password = rnd_username(), rnd_password()
        order_name = rnd_string(10)
        order_description = flag
        order_price = rnd_integer(101, 500)

        try:
            self.mch.register(session, username, password)
        except AssertionError:
            pass

        self.mch.login(session, username, password, Status.MUMBLE)
        self.mch.create_order(session, order_name, order_description, order_price)

        flag_id_mod = f"{username}:{password}:{order_name}"

        self.cquit(
            Status.OK,
            public=json.dumps({"username": username, "order_name": order_name}),
            private=flag_id_mod,
        )

    def get(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        fl = flag_id.split("\n")
        username, password, order_name = fl[0].split(":")

        self.mch.login(session, username, password, Status.CORRUPT)

        orders = self.mch.get_order(session, Status.CORRUPT)

        self.assert_in(
            order_name,
            orders,
            f"Order '{order_name}' not found in the list",
            Status.CORRUPT,
        )
        self.assert_in(
            flag,
            orders,
            f"Flag '{flag}' not found in the order description",
            Status.CORRUPT,
        )

        self.cquit(Status.OK)


if __name__ == "__main__":
    c = Checker(sys.argv[2])
    try:
        if sys.argv[1] == "info":
            c.info()
        else:
            c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
