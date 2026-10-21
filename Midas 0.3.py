import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import datetime as dt

def main():
    crypto_graph()
    
def get_crypto_price(crypto:str, currency:str='USDT'):
    key = "https://api.binance.com/api/v3/ticker/price?symbol=" + crypto + currency
    
    # requesting data from url
    data = requests.get(key)  
    data = data.json()
    
    return(data['price'])

def crypto_analysis(i, dates, prices):
    print(i)
    CRYPTO = 'BTC'
    price = get_crypto_price(CRYPTO)
    
    #Get minutes and seconds of the current hour.
    dates.append(dt.datetime.now().strftime('%M:%S'))
    prices.append(price)
    
    #Limit both axis to 20 items.
    dates = dates[-50:]
    prices = prices[-50:]
    
    #Clear x and y plot lists
    ax.clear()
    ax.plot(dates, prices)
    
    #Format plot:
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.1)

def crypto_graph():
    figure = plt.figure()
    global ax
    ax = figure.add_subplot(1, 1, 1)
    dates = []
    prices = []
    
    animate = animation.FuncAnimation(figure, crypto_analysis, fargs=(dates, prices), interval=500)
    plt.show()

if __name__ == '__main__':
    main()