import enum
from urllib import request
import numpy as np
import time
import requests
import os
import warnings 

VERSION = '0.8'
DATA_SPLITTING = 10
TRAINING_ITERATIONS = 10000

def Main():
    warnings.filterwarnings('ignore')
    
    # produceSets(1000)
    
    np.random.seed(1)
    
    #Layer 1, 5 neurons each with 3 inputs.
    layer1 = NeuronLayer(5, 3)
    
    #Layer 2, 2 neurons with 5 inputs:
    layer2 = NeuronLayer(2, 5)
    #Neuron 0 will be the "buying" neuron, neuron 1 the selling one and neuron 2 the wait one.
    
    # neural_network = NeuralNetwork(layer1, layer2)
    neural_network = loadNetwork()
    
    
    for i in range(100):
        print(i)
        neural_network = trainNeuralNetwork(neural_network)
        print('Accuracy:', neural_network.accuracy)

class NeuronLayer():
    def __init__(self, numberOfNeurons:int, numberOfInputsPerNeuron):
        self.synapticWeights = 2 * np.random.random((numberOfInputsPerNeuron, numberOfNeurons)) - 1

class NeuralNetwork():
    def __init__(self, layer1:NeuronLayer, layer2:NeuronLayer):
        self.layer1 = layer1
        self.layer2 = layer2
        
    def __sigmoid(self, x):
        result = 1 / (1 + np.exp(-x))
        return(result)
    
    def __sigmoidDerivative(self, x):
        result = x * (1 - x)
        return(result)
    
    def train(self, trainingSetInputs, trainingSetOutputs, trainingIterations:int):
        for iteration in range(trainingIterations):
            Layer1Output, Layer2Output = self.think(trainingSetInputs)
            
            #Calculate error for layer 2:
            Layer2Error = trainingSetOutputs - Layer2Output
            Layer2Delta = Layer2Error * self.__sigmoidDerivative(Layer2Output)
            
            #Calculate de error from layer 1
            Layer1Error = Layer2Delta.dot(self.layer2.synapticWeights.T)
            Layer1Delta = Layer1Error * self.__sigmoidDerivative(Layer1Output)
            
            #Calculate adjustment:
            Layer1Adjustment = trainingSetInputs.T.dot(Layer1Delta)
            Layer2Adjustment = Layer1Output.T.dot(Layer2Delta)
            
            #Adjust weights:
            self.layer1.synapticWeights += Layer1Adjustment
            self.layer2.synapticWeights += Layer2Adjustment
     
    def checkAccuarcy(self, inputSet, outputSet):
        outputs = self.think(inputSet)[1]
        
        correctGuess = 0
        for i, output in enumerate(outputs):
            if np.argmax(output) == np.argmax(outputSet[i]):
                correctGuess += 1
        accuracy = (correctGuess / i) * 100
        return(np.mean(accuracy))
            
    def think(self, inputs):
        Layer1Output = self.__sigmoid(np.dot(inputs, self.layer1.synapticWeights))
        Layer2Output = self.__sigmoid(np.dot(Layer1Output, self.layer2.synapticWeights))
        return(Layer1Output, Layer2Output)

def get_BTC_price():
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    
    data = requests.get(key)
    data = data.json()
    
    return(float(data['price']))

def collectData(lastTime=None, lastPrice=None, lastDerivative=None):
    if lastTime != None:
        try:
            BTCprice = get_BTC_price()
            currentTime = time.time()
            derivative = (BTCprice - lastPrice) / (currentTime - lastTime)
            secondDerivative = (derivative - lastDerivative) / (currentTime - lastTime)
            data = np.array([[BTCprice, derivative, secondDerivative]])
            return(data, lastTime)
        except:
            return(None)
    else:
        try:
            lastPrice = get_BTC_price()
            lastTime = time.time()
            
            BTCprice = get_BTC_price()
            currentTime = time.time()
            lastDerivative = (BTCprice - lastPrice) / (currentTime - lastTime)
            lastPrice = BTCprice
            lastTime = time.time()
            
            BTCprice = get_BTC_price()
            currentTime = time.time()
            derivative = (BTCprice - lastPrice) / (currentTime - lastTime)
            secondDerivative = (derivative - lastDerivative) / (currentTime - lastTime)
            data = np.array([[BTCprice, derivative, secondDerivative]])
            
            return(data, lastTime)
            
        except:
            return(None)

def createSet(size=256):
    Set = np.array([])
    data = collectData()
    if data != None:
        data, lastTime = data
        lastPrice = data[0][0]
        lastDerivative = data[0][1]
        Set = np.append(Set, [data])
    else:
        pass
    
    for iteration in range(size - 1):
        data = collectData(lastTime, lastPrice, lastDerivative)
        if data != None:
            data, lastTime = data
            lastPrice = data[0][0]
            lastDerivative = data[0][1]
            Set = np.append(Set, [data])
        else:
            iteration -= 1
    Set = np.reshape(Set, (size, 3))
    return(Set)

def saveSet(Set:np.array, id:int):
    np.save("Set_" + str(id), Set)

def loadSet(id:int):
    os.chdir('Sets ' + VERSION)
    Set = np.load('Set_' + str(id) + '.npy')
    os.chdir("..")
    return(Set)

def produceSets(number:int):
    os.chdir("Sets " + VERSION)
    current_files = len(os.listdir())
    for id in range(number):
        Set = createSet()
        saveSet(Set, id + current_files)
        print(id)
    os.chdir("..")
    
def loadSets(setsSize=256):
    os.chdir('Sets ' + VERSION)
    Sets = np.array([])
    for file in os.listdir():
        Sets = np.append(Sets, np.load(file))
    number_of_files = len(os.listdir())
    Sets = np.reshape(Sets, (setsSize * number_of_files, 3))
    os.chdir("..")
    return(Sets)

def setAnalysis(Set):
    #This will give us only the BTC prices over time.
    data = Set[:, 0]
    
    maximums = []
    minimums = []
    
    #Control variables for seeking out maximums and minimums
    before = ''
    for i, value in enumerate(data):
        if i == 0:
            pass
        else:
            if value < lastValue:
                if before == 'HIGHER':
                    maximums.append(i)
                before = 'LOWER'
            elif value >= lastValue:
                if before == 'LOWER':
                    minimums.append(i)
                before = 'HIGHER'
        lastValue = value
    
    # print('MAXIMUMS:', maximums)
    # print('MINIMUMS:', minimums)
    
    # 0 buying, 1 selling.
    correctOutput = np.array([])
    before = ''
    for i in range(len(data)):
        #In maximums the best is selling.
        if i in maximums:
            correctOutput = np.append(correctOutput, np.array([0, 1]))
            before = 'MAXIMUM' 
        elif i in minimums:
            correctOutput = np.append(correctOutput, np.array([1, 0]))
            before = 'MINIMUM'
        else:
            if before == 'MAXIMUM':
                correctOutput = np.append(correctOutput, np.array([0, 1]))
            elif before == 'MINIMUM':
                correctOutput = np.append(correctOutput, np.array([1, 0]))
            else:
                #  / Set[i + 1] The previous was a minimum
                # / Set[i]
                #/
                if data[i] < data[i+1]:
                    correctOutput = np.append(correctOutput, np.array([1, 0]))
                    before = 'MINIMUM'
                else:
                    correctOutput = np.append(correctOutput, np.array([0, 1]))
                    before = 'MAXIMUM'
    
    setsLength = int(len(correctOutput) / 2)
    correctOutput = np.reshape(correctOutput, (setsLength, 2))
    # print(correctOutput)
    return(correctOutput)

def trainNeuralNetwork(neural_network:NeuralNetwork):
    #First we load all the datasets:
    sets = loadSets()
    
    #After that, we divide Sets in 5 groups. To ensure that the number of sets is multiple of five
    #we discard the restant sets.
    setsSize = len(sets) - (len(sets) % DATA_SPLITTING)
    groupSize = int(setsSize / DATA_SPLITTING)
    #Control variable of number of training samples.
    training_sample_counter = 0
    error = np.array([])
    accuracy = 0
    for i in range(DATA_SPLITTING):
        trainingSets = np.array([])
        for j in range(DATA_SPLITTING):
            
            #This will be the testing sample
            if i == j:
                testingSets = sets[groupSize * i: groupSize * (i+1), :]
                testingSets = np.reshape(testingSets, (groupSize, 3))
            else:
                trainingSets = np.append(trainingSets, sets[groupSize * i: groupSize * (i+1), :])
        trainingSets = np.reshape(trainingSets, (groupSize * (DATA_SPLITTING - 1), 3))
        trainingOutputs = setAnalysis(trainingSets)
        neural_network.train(trainingSets, trainingOutputs, TRAINING_ITERATIONS)
        
        testingOutputs = setAnalysis(testingSets)
        accuracy += neural_network.checkAccuarcy(testingSets, testingOutputs)
    accuracy = accuracy / DATA_SPLITTING
    neural_network.accuracy = accuracy
    saveNetwork(neural_network)
    return(neural_network)
    
def saveNetwork(neural_network:NeuralNetwork):
    np.save("Layer1 " + VERSION, neural_network.layer1)
    np.save("Layer2 " + VERSION, neural_network.layer2)

def loadNetwork():
    layer1 = np.load("Layer1 " + VERSION + ".npy", allow_pickle=True)
    layer2 = np.load("Layer2 " + VERSION + ".npy", allow_pickle=True)
    neural_network = NeuralNetwork(layer1, layer2)
    
    return(neural_network)

if __name__ == '__main__':
    Main()