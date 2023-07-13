class General:
    counter_tx = [50, 50]  # количество транзакций для накрутки
    num_of_threads = 4  # количество кошельков, которое будет обрабатываться одновременно
    amount_ftm = 10  # количество ftm которое будет выводиться на кошелек для транзакций
    use_proxy = True  # хотим ли мы использовать прокси
    withdrawal_from_okx = True  # хотим ли мы пополнять с биржи
    max_retries = 3  # количество попыток при неудачной транзакции

    # OKX
    use_okx_proxy = True  # если не используете прокси, переведите в False
    okx_proxy = ""
    okx_apikey = ""
    okx_apisecret = ""
    okx_passphrase = ""
