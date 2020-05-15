FROM python:3.8.3-slim-buster
ENV LD_LIBRARY_PATH /usr/local/lib
RUN mkdir /breakout-trader
RUN mkdir /breakout-trader/config
WORKDIR /breakout-trader
COPY . /breakout-trader
RUN pip3 install -r requirements.txt --no-cache-dir
CMD [ "python3", "./bot.py" ]
