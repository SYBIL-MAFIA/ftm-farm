import threading
import concurrent.futures
from web3 import Web3
from abi.ff import con_abi
from abi.abi import abi
import concurrent.futures
import requests
import time
from config import General
import random
import queue

from ftm_withdraw import main_withdraw

keys_file = 'keys.txt'

proxies_file = 'proxies.txt'


def load_keys(file):
    with open(file, 'r') as f:
        keys = [line.strip() for line in f]
    return keys


def load_proxies(file):
    with open(file, 'r') as f:
        proxies = [line.strip() for line in f]
    return proxies


def get_web3(proxy, flag):
    session = requests.Session()
    if flag:
        session.proxies = {'http': proxy, 'https': proxy}
        web3 = Web3(Web3.HTTPProvider("https://rpc3.fantom.network", session=session))
    else:
        web3 = Web3(Web3.HTTPProvider("https://rpc3.fantom.network"))

    return web3


def make_transaction(private_key, proxy, counter_tx):
    web3 = get_web3(proxy, General.use_proxy)
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(
        address=web3.to_checksum_address("0xc5c01568a3b5d8c203964049615401aaf0783191"),
        abi=con_abi
    )
    address_bytes = bytes.fromhex(account.address[2:])
    address_bytes_32 = bytes(12) + address_bytes
    tx_data = (
        "0x000200000000000000000000000000000000000000000000000000000000000186a"
        "00000000000000000000000000000000000000000000000000000000000000000"
        f"{account.address[2:]}"
    )
    adapter_params_bytes = bytes.fromhex(tx_data[2:])

    for i in range(random.randint(counter_tx[0], counter_tx[1])):
        retries = 0
        max_retries = General.max_retries
        while retries < max_retries:
            try:
                value = contract.functions.estimateSendFee(
                    167,
                    address_bytes_32,
                    100000000000000,
                    True,
                    tx_data
                ).call()
                value = int(value[0])
                transaction = contract.functions.sendFrom(
                    account.address,
                    167,
                    address_bytes_32,
                    100000000000000,
                    (account.address, "0x0000000000000000000000000000000000000000", tx_data)
                ).build_transaction({
                    'from': account.address,
                    'nonce': web3.eth.get_transaction_count(account.address),
                    'gas': 500000,
                    'gasPrice': web3.to_wei('850', 'gwei'),
                    'chainId': 250,
                    'value': value
                })
                signed_tx = web3.eth.account.sign_transaction(transaction, private_key=private_key)
                tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
                if tx_receipt['status'] == 0:
                    raise Exception(f'Транзакция №{i + 1} включена в блокчейн, но завершилась с ошибкой')
                else:
                    print(f'Транзакция №{i + 1} Tx hash: https://ftmscan.com/tx/{tx_hash_1} | {account.address}')
                break  # Транзакция выполнена успешно, выходим из цикла
            except Exception as e:
                print(f"Ошибка при выполнении транзакции: {str(e)}")
                retries += 1
                if retries < max_retries:
                    print(f"Повторная попытка через 5 секунд...")
                    time.sleep(5)
                else:
                    print(
                        f"Достигнуто максимальное количество попыток. Не удалось выполнить транзакцию для {account.address}")
                    break


def send_requests(url):
    while True:
        response = requests.get(url)
        if response.status_code != 429:
            return response.json()
        retry_after = int(response.headers.get('Retry-After', 1))
        time.sleep(retry_after)


def buy_mim(private_key, proxy, amount):
    web3 = get_web3(proxy, General.use_proxy)
    amount = 1000000000000000000
    account = web3.eth.account.from_key(private_key)
    url = f'https://api-defillama.1inch.io/v5.0/250/swap?fromTokenAddress=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&toTokenAddress=0x82f0B8B456c1A451378467398982d4834b6829c1&amount={amount}&fromAddress={account.address}&slippage=3'
    print(url)
    retries = 0
    max_retries = General.max_retries
    while retries < max_retries:
        try:
            response = send_requests(url)
            tx = response['tx']
            tx['chainId'] = 250
            tx['nonce'] = web3.eth.get_transaction_count(account.address)
            tx['to'] = Web3.to_checksum_address(tx['to'])
            tx['gasPrice'] = int(tx['gasPrice'])
            tx['gas'] = int(int(tx['gas']))
            tx['value'] = int(tx['value'])

            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash = web3.to_hex(raw_tx_hash)

            print(f'Свапнул FTM for MIM via 1Inch Tx hash: https://ftmscan.com/tx/{tx_hash} | {account.address}')
            break

        except Exception as e:
            print(f"Ошибка при выполнении транзакции: {str(e)}")
            retries += 1

            if retries < max_retries:
                print(f"Повторная попытка через 5 секунд...")
                time.sleep(5)
            else:
                print("Достигнуто максимальное количество попыток. Не удалось выполнить транзакцию.")


def main_withdrawal_from_okx(proxy, private_key):
    web3 = get_web3(proxy, private_key)
    account = web3.eth.account.from_key(private_key)
    balance_cash = web3.eth.get_balance(account.address)

    main_withdraw(General.amount_ftm, account.address)
    print(f'Start waiting for deposit from okx | {account.address}')
    while True:
        time.sleep(4)
        balance = web3.eth.get_balance(account.address)

        if balance > balance_cash:
            print(f'Withdrawal from OKX done | {account.address}')
            break


def main(args):
    time.sleep(random.randint(10, 15))
    key, proxy = args
    if General.withdrawal_from_okx:
        main_withdrawal_from_okx(proxy.strip(), key.strip())
    buy_mim(key.strip(), proxy.strip(), General.amount_ftm)
    make_transaction(key.strip(), proxy.strip(), General.counter_tx)


if __name__ == '__main__':
    private_keys = load_keys(keys_file)
    proxies = load_proxies(proxies_file)
    args = zip(private_keys, proxies)

    with concurrent.futures.ThreadPoolExecutor(max_workers=General.num_of_threads) as executor:
        futures = {executor.submit(main, arg): arg for arg in args}

        for future in concurrent.futures.as_completed(futures):
            arg = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f'{arg} generated an exception: {exc}')
