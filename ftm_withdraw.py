import ccxt
from config import *
from web3 import Web3, HTTPProvider
from config import General
import time


def handle_ccxt_error(error):
    error_type = type(error).__name__
    print(f"  [OKX][NATIVE] Возникла ошибка {error_type}.")


def fetch_fee(exchange):
    try:
        currencies = exchange.fetch_currencies()

        if 'FTM' in currencies and 'Fantom' in currencies['FTM']['networks']:
            currencyInfo = currencies['FTM']
            networkInfo = currencyInfo['networks']['Fantom']
            fee = networkInfo['fee']
        else:
            fee = 0.5

        return fee

    except (ccxt.InsufficientFunds, ccxt.PermissionDenied, ccxt.AccountSuspended, ccxt.AuthenticationError,
            ccxt.BadResponse, ccxt.ExchangeError, ccxt.RateLimitExceeded, ccxt.DDoSProtection,
            ccxt.ExchangeNotAvailable, ccxt.RequestTimeout, ccxt.NetworkError, ccxt.BaseError) as e:
        handle_ccxt_error(e)


def withdraw(amount, address, exchange):
    fee = fetch_fee(exchange)
    print(f"Начинаю выводить {amount} FTM на {address}")

    retries = 0
    max_retries = General.max_retries
    while retries < max_retries:
        try:
            exchange.withdraw('FTM', amount, address,
                              params={
                                  "toAddress": address,
                                  "chainName": 'FTM-Fantom',
                                  "dest": 4,
                                  "fee": fee,
                                  "pwd": '-',
                                  "amt": amount,
                                  "network": 'Fantom'
                              })
            break

        except (ccxt.RateLimitExceeded, ccxt.InsufficientFunds, ccxt.PermissionDenied, ccxt.AccountSuspended,
                ccxt.AuthenticationError, ccxt.BadResponse, ccxt.ExchangeError, ccxt.DDoSProtection,
                ccxt.ExchangeNotAvailable, ccxt.RequestTimeout, ccxt.NetworkError, ccxt.BaseError) as e:

            if isinstance(e, ccxt.RateLimitExceeded):
                print("Превышен лимит запросов. Повторная попытка через 5 секунд...")
                time.sleep(5)
            else:
                handle_ccxt_error(e)

            retries += 1

    if retries == max_retries:
        print("Превышено максимальное количество попыток вывода.")


def main_withdraw(amount, address):
    exchange_options = {
        'apiKey': General.okx_apikey,
        'secret': General.okx_apisecret,
        'password': General.okx_passphrase,
        'enableRateLimit': True,
    }

    if General.use_okx_proxy:
        exchange_options['proxies'] = {
            'http': General.okx_proxy,
            'https': General.okx_proxy,
        }

    exchange = ccxt.okx(exchange_options)

    withdraw(amount, address, exchange)
