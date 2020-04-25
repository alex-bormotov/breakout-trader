import ccxt
import json
import time
import requests


def get_config():
    with open("config/config.json", "r") as read_file:
        return json.load(read_file)

def get_paper_balance():
    with open("config/paper_balance.json", "r") as read_file:
        return json.load(read_file)

def write_paper_balance(new_balance):
    with open("config/paper_balance.json", "w") as write_file:
        json.dump(new_balance, write_file, indent=1)


def notice(msg):
    if len(str(get_config()["telegram_chat_id"])) and len(get_config()["telegram_token"]) > 1:
        t = Telegram()
        t.send_message(msg)
    else:
        print(msg)

class Telegram:
    def __init__(self):
        self.chat_id = get_config()["telegram_chat_id"]
        self.token = get_config()["telegram_token"]

    def send_message(self, msg):
        try:
            requests.get(f"https://api.telegram.org/bot{self.token}/sendMessage?text={msg}&chat_id={self.chat_id}")
        except Exception as e:
            notice(str(e))


class Exchange:
    def __init__(self, coin_pair, coin, coin2):
        self.key = get_config()["exchange_key"]
        self.secret = get_config()["exchange_secret"]
        self.exchange = ccxt.binance({"apiKey": self.key, "secret": self.secret, "enableRateLimit": False})
        self.coin_pair = coin_pair
        self.coin = coin
        self.coin2 = coin2
        self.paper_enabled = get_config()["paper_trading"]


    def price(self):
        def get_price(self):
            try:
                return self.exchange.fetch_ticker(self.coin_pair)["last"]
            except Exception as e:
                notice(str(e))

        while True:
            price = get_price(self)
            if price is not None:
                return(price)


    def balance(self):
        try:
            if self.paper_enabled == "yes":
                return get_paper_balance()["paper_balance"]
            else:
                return [self.exchange.fetch_balance()[self.coin]["free"], self.exchange.fetch_balance()[self.coin2]["free"]]
        except Exception as e:
            notice(str(e))


    def order(self, amount, order_side):
        price = None
        params = {}
        # params = {'test': True}
        paper_price = self.price()
        try:
            if self.paper_enabled == "yes":
                if order_side == "sell":
                    new_balance_coin1 = get_paper_balance()["paper_balance"][0] - amount
                    new_balance_coin2 = get_paper_balance()["paper_balance"][1] + (paper_price * amount)
                    write_paper_balance({"paper_balance": [new_balance_coin1, new_balance_coin2]})
                    notice(f"Paper order {order_side} {amount} {self.coin} executed at price {paper_price} {self.coin2}")
                    return True
                elif order_side == "buy":
                    new_balance_coin1 = get_paper_balance()["paper_balance"][0] + amount
                    new_balance_coin2 = get_paper_balance()["paper_balance"][1] - (paper_price * amount)
                    write_paper_balance({"paper_balance": [new_balance_coin1, new_balance_coin2]})
                    notice(f"Paper order {order_side} {amount} {self.coin} executed at price {paper_price} {self.coin2}")
                    return True
            else:
                order = self.exchange.create_order(self.coin_pair, 'market', order_side.lower(), amount, price, params)
                notice(order)
                return order
        except Exception as e:
            notice(str(e))


class Trader:
    def __init__(self, coin_pair, coin, coin2):
        self.api_requests_frequency_per_second = get_config()["api_requests_frequency_per_second"]
        self.trailing_step_percent = get_config()["trailing_step_percent"]
        self.change_percent = get_config()["change_percent"]
        self.coin_pair = coin_pair
        self.exchange = Exchange(coin_pair, coin, coin2)


    def trail_stop(self, direction):
        start_price = self.exchange.price()
        last_change_percent = 0.0
        current_change_percent = 0.0

        while True:
            if direction == "long":
                if current_change_percent + self.trailing_step_percent >= last_change_percent:
                    last_change_percent = current_change_percent
                    price = self.exchange.price()
                    current_change_percent = ((price - start_price) / start_price) * 100
                    time.sleep(self.api_requests_frequency_per_second)
                    continue
                else:
                    return "sell"

            if direction == "short":
                if current_change_percent - self.trailing_step_percent <= last_change_percent:
                    last_change_percent = current_change_percent
                    price = self.exchange.price()
                    current_change_percent = ((price - start_price) / start_price) * 100
                    time.sleep(self.api_requests_frequency_per_second)
                    continue
                else:
                    return "buy"

    def breakout_detect(self):
        start_price = self.exchange.price()

        while True:
            current_price = self.exchange.price()
            change_percent = ((current_price - start_price) / start_price) * 100
            if change_percent > self.change_percent:
                return "up"
            elif change_percent < - self.change_percent:
                return "down"
            else:
                time.sleep(self.api_requests_frequency_per_second)
                continue


def main():
    coin_pair = get_config()["coin_pair"].upper()
    coin = coin_pair.split("/")[0].upper()
    coin2 = coin_pair.split("/")[1].upper()
    direction = get_config()["direction"]
    t = Trader(coin_pair, coin, coin2)
    e = Exchange(coin_pair, coin, coin2)

    if direction == "long":
        notice(f'{direction.upper()} Mode\nStarted at price {e.price()} {coin2}\nBalance is {e.balance()[1]} {coin2}')
        while True:
            if t.breakout_detect() == "down":
                order = e.order(e.balance()[1] / e.price(), "buy")
                if order is True:
                    if t.trail_stop(direction) == "sell":
                        amount = e.balance()[0]
                        e.order(amount, "sell")
                        notice(f'Balance is {e.balance()[1]} {coin2}')
                        main()
            else:
                continue

    elif direction == "short":
        notice(f'{direction.upper()} Mode\nStarted at price {e.price()} {coin2}\nBalance is {e.balance()[0]} {coin}')
        while True:
            if t.breakout_detect() == "up":
                order = e.order(e.balance()[0], "sell")
                if order is True:
                    if t.trail_stop(direction) == "buy":
                        amount = e.balance()[1] / e.price()
                        e.order(amount, "buy")
                        notice(f'Balance is {e.balance()[0]} {coin}')
                        main()
            else:
                continue


if __name__ == "__main__":
    main()
