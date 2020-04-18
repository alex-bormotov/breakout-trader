import ccxt
import json
import time
import requests


def get_config():
    with open("config.json", "r") as read_file:
        return json.load(read_file)
    

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
    def __init__(self):
        self.key = get_config()["exchange_key"]
        self.secret = get_config()["exchange_secret"]
        self.exchange = ccxt.binance({"apiKey": self.key, "secret": self.secret, "enableRateLimit": False})
        self.coin_pair = get_config()["coin_pair"]
        self.paper_enabled = get_config()["paper_trading"]
        self.paper_balance = get_config()["paper_balance"]
      
        
    def price(self):
        def get_price(self):
            try:
                return self.exchange.fetch_ticker(self.coin_pair.upper())["last"]
            except Exception as e:
                notice(str(e))

        while True:
            price = get_price(self)
            if price is not None:
                return(price)


    def balance(self):
        coin = self.coin_pair.split("/")[0]
        coin2 = self.coin_pair.split("/")[1]      
        try:
            if self.paper_enabled == "yes":
                return self.paper_balance
            else:
                return [self.exchange.fetch_balance()[coin.upper()]["free"], self.exchange.fetch_balance()[coin2.upper()]["free"]]
        except Exception as e:
            notice(str(e))


    def order(self, amount, order_side):
        self.order_side = order_side
        price = None
        params = {}
        # params = {'test': True}
        try:
            if self.paper_enabled == "yes":
                if order_side == "sell":
                    coin = self.coin_pair.split("/")[0]
                    sell_price = self.price()
                    self.paper_balance[0] -= amount
                    self.paper_balance[1] += ((sell_price * amount) * 0.999)
                    # * 0.999 - 0.10% maker/taker fee without BNB
                    notice(f"Paper order {order_side} {amount} {coin} executed at price {sell_price}")
                elif order_side == "buy":
                    coin = self.coin_pair.split("/")[1]
                    buy_price = self.price()
                    self.paper_balance[0] += ((amount / buy_price) * 0.999)
                    self.paper_balance[1] -= amount
                    notice(f"Paper order {order_side} {amount} {coin} executed at price {buy_price}")
            else:
                order = self.exchange.create_order(self.coin_pair.upper(), 'market', self.order_side.lower(), amount, price, params)
                notice(order)
        except Exception as e:
            notice(str(e))


class Trader:
    def __init__(self):
        self.api_requests_frequency_per_second = get_config()["api_requests_frequency_per_second"]
        self.trailing_step_percent = get_config()["trailing_step_percent"]
        self.change_percent = get_config()["change_percent"]
        self.coin_pair = get_config()["coin_pair"]
        self.exchange = Exchange()

    
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
        notice(f"start_price {start_price}\nstarted")
 
        while True:
            current_price = self.exchange.price()
            change_percent = ((current_price - start_price) / start_price) * 100
            if change_percent > self.change_percent:
                notice(f"change_percent {change_percent}\ncurrent_price {current_price}\nPrice UP")
                return "up"
            elif change_percent < - self.change_percent:
                notice(f"change_percent {change_percent}\ncurrent_price {current_price}\nPrice DOWN")
                return "down"
            else:
                time.sleep(self.api_requests_frequency_per_second)
                continue
            

def main():
    pass






if __name__ == "__main__":
    main()
