import requests
import matplotlib.pyplot as plt
import time

def main():
    prices = []
    date = []
    startingTime = time.time
    for i in range(10):
        BTC = get_crypto_price('BTC')
        prices.append(BTC)
        date.append(i)
        print(i)
    plt.plot(date, prices)
    plt.show()
    
def get_crypto_price(crypto:str, currency:str='USDT'):
    key = "https://api.binance.com/api/v3/ticker/price?symbol=" + crypto + currency
    
    # requesting data from url
    data = requests.get(key)  
    data = data.json()
    
    return(data['price'])


if __name__ == '__main__':
    main()