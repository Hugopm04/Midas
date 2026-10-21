import enum
import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import datetime as dt
import statistics as stat
import numpy as np
import math
import pathlib

VERSION = '0.7'
#Control variable for loading qValues
LOAD = True

LOGFILE = ""
f = open("Logfile.txt", "w")
f.write(LOGFILE)
f.close()

class Inversion():
    def CalcProfit(self, btcPrice):
        #If the price when you bought was higher, that means you lost money.
        priceDifference = self.BtcPrice - btcPrice
        if self.buy:
            profit = (-priceDifference) * self.quantity
        #But if the price when you sold is higher, that means you won money.
        else:
            profit = priceDifference * self.quantity
        return(profit)
    
    def __init__(self, inversion:float, buy:bool, BtcPrice:float):
        #Money invested
        self.inversion = inversion
        
        #Control variable, if true, we are buying, if false, selling.
        self.buy = buy
        
        #Starting price of Bitcoin:
        self.BtcPrice = BtcPrice
        self.quantity = inversion / BtcPrice
        
        #Result of the operation
        self.result = 0
        
        #Moves implied in the inversion
        self.actions = []
    
def main():
    AI_Training()
    
def get_crypto_price(crypto:str, currency:str='USDT'):
    key = "https://api.binance.com/api/v3/ticker/price?symbol=" + crypto + currency
    
    # requesting data from url
    data = requests.get(key)  
    data = data.json()
    
    return(data['price'])

def selectInterval(array:list, number:float, upperBound=True, lowerBound=True):
    '''upperBound and lowerBound determines wether the number can be at the right 
    or the left of the array.'''
    for i, item in enumerate(array):
        if lowerBound:
            if number < item:
                return(i)
        else:
            if i != 0:
                if number < item:
                    return(i - 1)
                
        if upperBound and i == (len(array) - 1):
            if number > item:
                if lowerBound:
                    return(i + 1)
                else:
                    return(i)
                
def chooseRowOpen(derivate:float, derivateMean:float, priceVariance:float):
    
    #In case we are currently doing nothing:
    
    #Derivates will have 11 groups:
    # A B C D E F G H I J K
    
    #Derivate Mean 9:
    # A B C D E F G H I
    
    #And Price Variance 5:
    # A B C D E
    
    '''
    This will be a problem of numerical bases, or so I see it.
    Let's take just Derivate Mean and Price Variance groups for the example.
    A cool way to organize the rows is to make Price Variance groups "units".
    So in this case Prince Variance groups will be equivalent to:
    A = 0, B = 1, C = 2, D = 3, E = 4
    And each Derivate Mean will count as a multiple of 5, becouse there are 5 possible states of price
    Variation for each Derivate Mean state. Resulting in:
    A = 5 * 0, B = 5 * 1, C = 5 * 2, D 5 * 3...
    This way the fisrt row, (Derivate Mean state = A and Price Variance state = A) or (AA) where the
    fisrt A is the state of the Derivate Mean and the second one the state of the Price Variance,
    has the value: 5 * 0 + 0 = 0
    Wich is perfect as it is the fisrt elemnt of the array. Another row value: (BC)
    5 * 1 + 2 = 7, if the list is something like this : [AA, AB, AC, AD, AE, BA, BB, BC]
    You can see that 7 corresponds with the BC row.
    Applying this concept we can expand the system for derivates too, and they values will be
    multiples of 45, as there are 45 elements per each derivate state.
    A = 45 * 0, B = 45 * 1, C = 45 * 2, D 45 * 3...
    For example, the combination of states (CHE) would be:
    45 * 2 + 5 * 7 + 4 = 129.
    '''
    
    priceVarianceStates = [0.01, 5, 10, 15, 30]
    priceVarianceValues = [i for i in range(len(priceVarianceStates))]
    
    meanStates = [-30, -15, -10, -5, 5, 10, 15, 30]
    meanMultiple = len(priceVarianceStates)
    meanValues = [i * meanMultiple for i in range(len(meanStates) + 1)]
    
    
    derivateStates = [-50, -20, -15, -10, -5, 5, 10, 15, 20, 50]
    derivateMultiple = meanMultiple * (len(meanStates) + 1)
    derivateValues = [i * derivateMultiple for i in range(len(derivateStates) + 1)]
    
    priceVarianceValue = selectInterval(priceVarianceStates, priceVariance, lowerBound=False)
    priceVarianceValue = priceVarianceValues[priceVarianceValue]
    
    meanValue = selectInterval(meanStates, derivateMean)
    meanValue = meanValues[meanValue]
    
    derivateValue = selectInterval(derivateStates, derivate)
    derivateValue = derivateValues[derivateValue]
    
    row = derivateValue + meanValue + priceVarianceValue
    return(row)

def chooseRowClose(derivate:float, profit:float, buy:bool):
    '''But if we have already bought or sold something, we can either wait or close the action.
    #That means we are going to need another array for this cases. The AI will receive as
    data the current profit of the operation and the derivate of the price of BTC. Both will
    have 15 possible states each. Giving an array of 450 elements.
    '''
    profitStates = [-50, -30, -20, -15, -10, -5, -2, 2, 5, 10, 15, 20, 30, 50]
    profitValues = [i for i in range(len(profitStates) + 1)]
    
    derivateStates = [-50, -30, -20, -15, -10, -5, -2, 2, 5, 10, 15, 20, 30, 50]
    derivateMultiple = len(profitStates) + 1
    derivateValues = [i * derivateMultiple for i in range(len(derivateStates) + 1)]
    
    profitValue = selectInterval(profitStates, profit)
    profitValue = profitValues[profitValue]
    
    derivateValue = selectInterval(derivateStates, derivate)
    derivateValue = derivateValues[derivateValue]
    
    if buy:
        row = derivateValue + profitValue
    else:
        row = derivateValue + profitValue + 15*15
    return(row)
 
def getAction(row, open:bool):
    
    if open:
        # 0 is to buy, 1 to sell, and 2 do nothing.
        if np.random.random() < epsilon:
            choice = np.argmax(OpenQValues[row])
        else:
            choice = np.random.randint(3)
        return(choice)

    else:
        # 0 is to close the action, 1 to wait.
        if np.random.random() < epsilon:
            choice = np.argmax(CloseQValues[row])
        else:
            choice = np.random.randint(2)
        return(choice)

def save():
    np.save("OpenQValues" + VERSION, OpenQValues)
    np.save("CloseQValues" + VERSION, CloseQValues)

def load():
    global OpenQValues
    global CloseQValues
    OpenQValues = np.load("OpenQValues" + VERSION)
    CloseQValues = np.load("CloseQValues" + VERSION)
 
def AI_Training():
    
    global LOGFILE
    
    #Data collection    
    CRYPTO = 'BTC'
    ITEMS_PER_LIST = 50
    ITERATIONS = 1000000
    SAVING_INTERVALS = 20
    COMISSION = 0.003
    INITIAL_MONEY = 100
    INVESTING_BASE_MONEY = 40
    
    DERIVATE_AMPLIFIER = 10
    DERIVATE_MEAN_AMPLIFIER = 10
    PROFIT_AMPLIFIER = 10**5 / 2
    
    
    prices = np.array([])
    derivateArray = np.array([])
    
    #Control variable for derivate calculus.
    previousTime = time.time()
    
    funds = INITIAL_MONEY
    totalMoney = INITIAL_MONEY
    
    #Control variable to know whether the AI has lost all it's money.
    restart = False
    
    #Control variables to check if the AI is currently performing any action:
    buying = False
    selling = False
    
    #Control variable for security copies.
    savingIntervals = SAVING_INTERVALS
    
    #AI schematic:
    '''
    The AI will receive the derivate of the price, the mean of the derivate and the price variance.
    As it is a punish and reward AI, it will have a "table of memories".
    This table will have 495 rows, with 3 columns each.
    This is becouse we agroup the possible states with intervals, for example:
    In the derivate, being between 10 and 0 is one of the intervals.
    So the different states in the different types of data are:
    Derivates: (11 possible states)
    x < -50, x < -20, x < -15, x < -10, x < -5, x > 5, x > 10, x > 15, x > 20, x > 50 and x between
    -5 and 5.
    
    Derivate Mean: (9 possible states)
    x < -30, x < - 15, x < -10, x < -5, x > 5, x > 10, x > 15, x > 30 and x between -5 and 5.
    
    Price Variance: (5 possible states)
    x > 0, x > 5, x > 10, x > 15, x > 30
    
    Each row has assigned one of the 495 possible combinations of states, being an example:
    5 < Derivate < 10 & -15 < Derivate Mean < -10 & 15 < Price Variation < 30
    This row will have 3 columns, each one containing the "memories" of the three possible actions in
    this precise state (sell, buy or do nothing).
    
    In order to assing a row to each state, there will be a function.
    '''
    
    #AI variables
    global OpenQValues
    OpenQValues = np.zeros((495, 3))
    global CloseQValues
    CloseQValues = np.zeros((450, 2))
    
    global epsilon
    epsilon = 0.8
    global discountFactor
    discountFactor = 0.8
    global learningRate 
    learningRate = 0.9
    
    for i in range(ITERATIONS):
        try:
            price = float(get_crypto_price(CRYPTO))
        except:
            pass
        
        if restart:
            restart = False
            i = 0
        
        #Data recopilation
        
        if len(prices) > 1:
            lastPrice = prices[-1]
            difference = lastPrice - price
            
            currentTime = time.time()
            derivate = difference / (currentTime - previousTime)
            previousTime = currentTime
            
            derivateArray = np.append(derivateArray, derivate)       
            
            #Limit derivate list number of items:
            derivateArray = derivateArray[-ITEMS_PER_LIST:]

            #Mean
            derivateMean = np.mean(derivateArray)
        
        prices = np.append(prices, price)
        priceVariance = np.var(prices)
            
        #Limit prices list:
        prices = prices[-ITEMS_PER_LIST:]
        
        #This way all the list are filled before training.
        if i > ITEMS_PER_LIST:
            LOGFILE += "BTC price: " + str(price) + "\n"
            if i > savingIntervals:
                savingIntervals += SAVING_INTERVALS
                save()

            #If we aren't performing any action:
            if buying == False and selling == False:
                row = chooseRowOpen(derivate * DERIVATE_AMPLIFIER, derivateMean * DERIVATE_MEAN_AMPLIFIER, priceVariance)
                action = getAction(row, True)
                '''
                The AI can either buy or sell, and can't perform any other action until it closes the
                fisrt one. He will be able to use up to 2/3 of the money.
                '''
                #It wants to buy or sell:
                if action != 2:
                    #If it has, let's see how much it can spend:
                    disponible = funds / 3
                    
                    #Now according to the qValue of that row, it will buy more or less.
                    qValue = OpenQValues[row][0]
                    if qValue > 0:
                        quantity = INVESTING_BASE_MONEY * math.log(qValue + 1, math.e)
                        if quantity >= disponible:
                            inversion = disponible
                        else:
                            inversion = quantity
                        funds -= inversion + inversion * COMISSION
                        
                    #When the qvalue is lower, it reduces the quantity of inversion.
                    elif qValue <= 0:
                        quantity = INVESTING_BASE_MONEY / (math.log(-qValue + 1, math.e) + 1)
                        if quantity > disponible:
                            inversion = disponible
                        else:
                            inversion = quantity
                        funds -= inversion + inversion * COMISSION
                        
                    #If he wants to buy:
                    if action == 0:
                        #We store all the data of the move
                        inversionData = Inversion(inversion, True, price)
                        buying = True
                        LOGFILE += "I chose to buy " + str(inversion) + " BTC\n"
                    #If selling:
                    elif action == 1:
                        selling = True
                        inversionData = Inversion(inversion, False, price)
                        LOGFILE += "I chose to sell " + str(inversion) + " BTC\n"
                    #After the inversion we store the move in a list for further learning.
                    inversionData.actions.append([row, action])
                else:
                    LOGFILE += "I chose do nothing.\n"
            
            else:
                row = chooseRowClose(derivate * DERIVATE_AMPLIFIER, profit * PROFIT_AMPLIFIER, buying)
                action = getAction(row, False)
                #If it wants to close the action
                if action == 0:
                    inversionData.actions.append([row, action])
                    profit = inversionData.CalcProfit(price)
                    funds += inversionData.inversion + profit
                    
                    if buying:
                        LOGFILE += "I chose to close my bought with a profit of " + str(profit) + "$\n"
                    elif selling:
                        LOGFILE += "I chose to close my sold with a profit of " + str(profit) + "$\n"
                    
                    buying = False
                    selling = False
                    
                    
                    
                    #And we start the learning process:
                    #Fisrt we will train the OpenQValues section.
                    row, column = inversionData.actions.pop(0)
                    oldqValue = OpenQValues[row][column]
                    temporalDifference = profit + (discountFactor * np.max(OpenQValues[row])) - oldqValue
                    newqValue = oldqValue + (learningRate * temporalDifference)
                    OpenQValues[row][column] = newqValue
                    
                    #After that we can go for the close q values:
                    for row, column in inversionData.actions:
                        oldqValue = CloseQValues[row][column]   
                        temporalDifference = profit + (discountFactor * np.max(CloseQValues[row])) - oldqValue
                        newqValue = oldqValue + (learningRate * temporalDifference)
                        CloseQValues[row][column] = newqValue
                else:
                    #We check if we are winning or loosing money by holding, and punish or reward the AI for doing so.
                    profit = inversionData.CalcProfit(price)
                    if profit <= 0:
                        reward = - 10 ** (-4)
                    else:
                        reward = 10 ** (-4)
                    
                    LOGFILE += "I chose to hold my actual position with a profit of " + str(profit) + "$\n"
                    
                    oldqValue = CloseQValues[row][action]   
                    temporalDifference = reward + (discountFactor * np.max(CloseQValues[row])) - oldqValue
                    newqValue = oldqValue + (learningRate * temporalDifference)
                    CloseQValues[row][action] = newqValue
                    
                    inversionData.actions.append([row, action])
            
            #We punish the Ai for doing nothing to incentivate activity:
            if action == 2:
                reward = - 10 ** (-4)
                oldqValue = OpenQValues[row][action]
                temporalDifference = reward + (discountFactor * np.max(OpenQValues[row])) - oldqValue
                newqValue = oldqValue + (learningRate * temporalDifference)
                OpenQValues[row][action]
            
            #If it isn't selling or buying:
            if buying == False and selling == False:
                totalMoney = funds
            else:
                profit = inversionData.CalcProfit(price)
                totalMoney = funds + inversionData.inversion + profit
            #If he has lost too much money we restart the AI
            if funds <= (20):
                funds = INITIAL_MONEY
                totalMoney = INITIAL_MONEY
                restart = True
        
        LOGFILE += "\n"
        f = open("Logfile.txt", "a")
        f.write(LOGFILE)
        f.close()
        print(totalMoney)
        
        if totalMoney > 100:
            breakpoint()
               
        # if i > 60:
            # print('Derivate:', derivate * DERIVATE_AMPLIFIER)
            # print('Derivate Mean:', derivateMean * DERIVATE_MEAN_AMPLIFIER)
            # print('Varianza del precio:', priceVariance)
            # print('Profit:', profit * PROFIT_AMPLIFIER)
            # time.sleep(1)

if __name__ == '__main__':
    main()