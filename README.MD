# Transaction Boosting Script for Increasing Account Ratings

Script for boosting transactions, which can help increase the ratings of your accounts. 
The script is based on the FTM→MIM token pair and includes additional features that allow you 
to run it for a large account farm.

## Script Features:

1. Multithreading: You can now run the script simultaneously for multiple wallets.
2. Support for withdrawing FTM from your OKX account to all FTM wallets for script usage.
3. Purchase of MIM through 1inch.
4. Proxy support (optional).

## Instructions for Running the Script:
1. 
```commandline
pip install -r requirements.txt
```
or 
```commandline
pip install ccxt Requests web3
```
2. Purchase FTM on an exchange.
3. Add private keys in keys.txt and proxies in proxies.txt for the wallets.
4. Configure the script's settings, such as the number of transactions, number of threads, withdrawal volume, and other parameters.
5. Run 1cent.py
```commandline
python3 1cent.py
```

### Note:

The script will continue running as long as there is sufficient FTM on the wallets to cover the gas fees.

Telegram: https://t.me/retrodropTools
