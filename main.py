import requests
import pandas as pd

currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 'NZD']
exchange_rate_cache = {}


def get_currency_rate(from_currency, to_currency):
    if from_currency == to_currency:
        return 1.0
    elif (from_currency, to_currency) in exchange_rate_cache:
        return exchange_rate_cache[(from_currency, to_currency)]
    else:
        url = f'https://v6.exchangerate-api.com/v6/0b91e568f5592bfa05e1f9ca/latest/{from_currency}'
        response = requests.get(url)

        if response.status_code == 200:
            for currency in currencies:
                if currency == from_currency:
                    continue
                rate = response.json()['conversion_rates'][currency]
                exchange_rate_cache[(from_currency, currency)] = rate
                exchange_rate_cache[(currency, from_currency)] = 1 / rate
            return exchange_rate_cache[(from_currency, to_currency)]
        else:
            return Exception('Error retrieving currency rate: ' + str(response.status_code))


def format_profit(amount2):
    profit = format(amount2, '.4f').split('.')[1]
    if len(profit) == 2:
        profit = 0
    elif len(profit) == 3:
        profit = float('0.00' + profit[2] + '0')
    else:
        profit = float('0.00' + profit[2] + profit[3])
    return profit


while True:
    amount_input = input('Enter amount (or "quit" to exit): ')
    if amount_input == 'quit':
        break
    try:
        amount = float(amount_input)
    except ValueError:
        print('Invalid input')
        continue
    from_currency = input('Enter currency to convert from: ').upper()
    to_currency = input('Enter currency to convert to: ').upper()

    if from_currency not in currencies or to_currency not in currencies:
        print('Invalid currency')
        exit(1)
    elif from_currency == to_currency:
        print('Same currency')
        exit(1)

    df = pd.DataFrame(
        columns=["Currency", f"{from_currency} to intermediary", f"Intermediary to {to_currency}", "Profit"])

    customer_currency = None
    customer_amount = 0

    owner_currency = None
    owner_profit = 0

    for currency in currencies:
        if currency == from_currency or currency == to_currency:
            continue
        try:
            exchange_rate1 = get_currency_rate(from_currency, currency)
            amount1 = amount * exchange_rate1
        except Exception as e:
            print(e)
            break

        exchange_rate2 = get_currency_rate(currency, to_currency)
        amount2 = amount1 * exchange_rate2

        profit = format_profit(amount2)

        if profit > owner_profit:
            owner_profit = profit
            owner_currency = currency

        if amount2 > customer_amount:
            customer_amount = amount2
            customer_currency = currency
        new_row = ({"Currency": currency, f"{from_currency} to intermediary": format(amount1, '.4f'),
                    f"Intermediary to {to_currency}": format(amount2, '.4f'), "Profit": profit})
        df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)

    print(df.to_string(index=False))

    try:
        print('Best currency for customer: ' + customer_currency + ' with amount: ' + format(customer_amount, '.3f'))
        print('Best currency for owner: ' + owner_currency + ' with profit: ' + str(owner_profit))
    except Exception as e:
        print(e)
