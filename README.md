# Trading bot for Binance with breakout trading strategy

![](https://github.com/alex-bormotov/breakout-trader/workflows/Breakout-Trader-CI-CD/badge.svg) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/fba75048f4064497a458704194a6e927)](https://www.codacy.com/manual/alex-bormotov/breakout-trader?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alex-bormotov/breakout-trader&amp;utm_campaign=Badge_Grade)

## Disclaimer

> This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHOR AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

> Always start by running a trading bot in Paper trading mode and do not engage money before you understand how it works and what profit/loss you should expect.

### Features

> Breakout strategy - after starting the bot will be waiting for huge price movements and when it happened bot immediately bought the coin, and after that starts trailing stop loss for taking a profit. For example - if price down by 20% lasts 5 minutes bot detects it and immediately buys the coin and starts trailing stop loss when trailing step will be achieved bot execute sell order. This works because after any huge price movement immediately starts price correction in the opposite direction.

> Paper trading.

> Telegram notifications.

> Possibilities use "Long" or "Short" trade directions.

#### Install (Ubuntu + Docker)

```bash
git clone https://github.com/alex-bormotov/breakout-trader
```

```bash
cd breakout-trader
```

```bash
cp config/config.json.sample config/config.json
```

> Edit config/config.json

> Set paper balance in config/paper_balance.json

```bash
sudo chmod +x docker_ubuntu_install.sh && sudo ./docker_ubuntu_install.sh
```

```bash
sudo docker run -d --rm --mount src=`pwd`/config,target=/breakout-trader/config,type=bind skilfulll1/breakout-trader:latest
```

##### Say Me Thanks :)

> [My Binance Referal Link](https://www.binance.com/en/register?ref=35560900)

> BTC 1LTwU8hVYxxpHUDf3wYNDjnS9kK4PDdtgT

> ETH 0x23913F4ab3839a8b7bB987F348b8d974C045Dd17
