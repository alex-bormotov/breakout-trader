FROM python:3.8.2-slim-buster

ENV LD_LIBRARY_PATH /usr/local/lib

RUN apt-get update && apt-get install -y python3-pip
RUN mkdir /breakout-trader
RUN mkdir /breakout-trader/config

WORKDIR /breakout-trader

COPY . /breakout-trader

RUN pip3 install -r requirements.txt --no-cache-dir

CMD [ "python3", "./bot.py" ]