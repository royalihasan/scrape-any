
from decimal import Decimal
from price_parser import Price


def price_cleaner(price_text):
    price = Price.fromstring(price_text)
    return {
        'amount': price.amount,
        'currency': price.currency
    }


if __name__ == '__main__':
    print(price_cleaner("$3.99 /ea").get('amount'))
