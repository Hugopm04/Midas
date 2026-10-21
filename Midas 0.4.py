import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import datetime as dt

from scipy.fftpack import diff

def main():
    crypto_graph()
    
def get_crypto_price(crypto:str, currency:str='USDT'):
    key = "https://api.binance.com/api/v3/ticker/price?symbol=" + crypto + currency
    
    # requesting data from url
    data = requests.get(key)  
    data = data.json()
    
    return(data['price'])

def crypto_analysis(i, dates, prices, derivateDates, derivate):
    print(i)
    CRYPTO = 'BTC'
    ITEMS_PER_CHART = 50
    price = get_crypto_price(CRYPTO)
    if len(prices) > 0:
        lastPrice = float(prices[-1])
        difference = lastPrice - float(price)
        currentTime = time.time()
        speed = difference / (currentTime - previousTime)
        
        derivateDates.append(dt.datetime.now().strftime('%M:%S'))
        derivate.append(speed)       
         
        #Limit derivate list number of items:
        derivateDates = derivateDates[-ITEMS_PER_CHART:]
        derivate = derivate[-ITEMS_PER_CHART:]

        DerivateAxe.clear()
        DerivateAxe.plot(derivateDates, derivate)
        
    #Get minutes and seconds of the current hour.
    dates.append(dt.datetime.now().strftime('%M:%S'))
    prices.append(price)
    
    #Limit both axis to x items.
    dates = dates[-ITEMS_PER_CHART:]
    prices = prices[-ITEMS_PER_CHART:]
    
    #Clear x and y plot lists
    pricesAxe.clear()
    pricesAxe.plot(dates, prices)
    
    #Format plot:
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.01)

def crypto_graph():
    CRYPTO = 'BTC'

    
    CryptoChart = plt.figure(num= CRYPTO + ' analysis chart')
    global pricesAxe
    pricesAxe = CryptoChart.add_subplot(221)
    global DerivateAxe
    DerivateAxe = CryptoChart.add_subplot(222)
    
    pricesAxe.title.set_text(CRYPTO + ' price')
    DerivateAxe.title.set_text('Grow rate')
        
    # pricesAxe = CryptoChart.add_subplot(1, 1, 1)
    dates = []
    prices = []
    derivateDates = []
    derivate = []
    global previousTime
    previousTime = time.time()
    
    CryptoChartAnimation = animation.FuncAnimation(CryptoChart, crypto_analysis, fargs=(dates, prices, derivateDates, derivate), interval=500)
    
    plt.show()

if __name__ == '__main__':
    main()