import requests


def main():
    BTC_price = get_crypto_price('BTC')
    print(BTC_price)

def get_crypto_price(crypto:str, currency:str='USDT'):
    key = "https://api.binance.com/api/v3/ticker/price?symbol=" + crypto + currency
    
    # requesting data from url
    data = requests.get(key)  
    data = data.json()
    
    return(data['price'])

if __name__ == '__main__':
    main()