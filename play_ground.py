from decimal import Decimal
from price_parser import Price
price = Price.fromstring("$3.99 /ea")

print(type(price.amount))

print(price.currency)