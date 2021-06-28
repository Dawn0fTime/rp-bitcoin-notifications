#!/bin/python3
# bitcoin_notifications.py

# Based on the Python Project for Beginners: Bitcoin Price Notifications
# tutorial by Rok Novosel for Real Python.  Some changes have been made
# to reflect the changes to the CoinMarketCap API.

import requests
import time
from datetime import datetime

from requests import Session, Timeout, TooManyRedirects

BITCOIN_PRICE_THRESHOLD = 100000  # Set this to whatever you like
BITCOIN_API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/' \
                  'listings/latest'
parameters = {
    'start': '1',
    'limit': '100',
    'convert': 'USD',
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '{your-CMC-API-key}',
}
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/' \
                     '{your-IFTTT-key}'


def get_latest_bitcoin_price():
    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(BITCOIN_API_URL, params=parameters)
        response_json = response.json()
        return float(response_json['data'][0]['quote']['USD']['price'])
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def post_ifttt_webhook(event, value):
    # The payload that will be sent to the IFTTT service
    data = {'value1': value}
    # Inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def format_bitcoin_history(bitcoin_history):
    rows = []
    for bitcoin_price in bitcoin_history:
        # Formats the date into a string: '24.02.2018 15:09'
        date = bitcoin_price['date'].strftime('%d.%m.%Y %H:%M')
        price = bitcoin_price['price']
        # 24.02.2018 15:09: $<b>10123.4</b>
        row = '{}: $<b>{}</b>'.format(date, price)
        rows.append(row)

    # Use a <br> (break) tag to create a new line
    # Join the rows delimited by <br> tag: row1<br>row2<br>row3
    return '<br>'.join(rows)


def main():
    bitcoin_history = []
    while True:
        price = get_latest_bitcoin_price()
        date = datetime.now()
        bitcoin_history.append({'date': date, 'price': price})

        # Send an emergency notification
        if price < BITCOIN_PRICE_THRESHOLD:
            post_ifttt_webhook('bitcoin_price_emergency', price)

        # Send a Telegram notification
        # Once we have 5 items in our bitcoin_history send an update
        if len(bitcoin_history) == 5:
            post_ifttt_webhook('bitcoin_price_update',
                               format_bitcoin_history(bitcoin_history))
            # Reset the history
            bitcoin_history = []

        # Sleep for 5 minutes
        time.sleep(5 * 60)


if __name__ == '__main__':
    main()
