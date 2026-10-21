from dis import dis
import enum
from faulthandler import disable
from re import I
from urllib import request
import numpy as np
import time
import requests
import os
import warnings 
from multiprocessing import Process, Pool

VERSION = '0.9'
DATA_SPLITTING = 2
TRAINING_ITERATIONS = 20
GEN_SIZE = 5


def Main():
    warnings.filterwarnings('ignore')
    
    # training_inputs = np.array([[1, 1, 0, 0],
    #                             [10, 2, 3, 4],
    #                             [0, 2, 3, 4],
    #                             [1, 1, 1, 1],
    #                             [-2, 1, 3, 4]])
    
    # training_outputs = np.array([[1, 1, 0, 1, -1]]).T
    
    # neural_network = NeuralNetwork(np.array([[6, 3], [2, 6], [2, 2]]))
    # neural_network.train(training_inputs, training_outputs, 100)
    # accuracy = testNeuralNetwork(neural_network)
    
    produceAnalysis(version='0.8')
    
    neural_network = create_starting_generation()[0]
    # testNeuralNetwork(neural_network)
    
    # time.perf_counter()
    # AnalyzeSets('0.8')
    # print(time.perf_counter())
    
    # time.perf_counter()
    # Sets = loadSets(version='0.8')
    # setAnalysis(Sets)
    # print(time.perf_counter())
    
    time.perf_counter()
    inputs = loadSets(version='0.8')
    outputs = loadAnalysis(version='0.8')
    accuracy = neural_network.train(inputs, outputs, 5)
    print(time.perf_counter(), accuracy)
    
    time.perf_counter()
    os.chdir("Analyzed 0.8")
    accuracys = np.array([])
    for i, output in enumerate(os.listdir()):
        os.chdir("..")
        input = loadSet(id=i, version='0.8')
        output = loadAnalyzed(id=i, version='0.8')
        accuracy = np.append(accuracy, neural_network.train(input, output, 5))
    accuracy = np.mean(accuracys)
    print(time.perf_counter(), accuracy)
    
    naturalSelection()

class NeuronLayer():
    def __init__(self, distribution:np.array):
        '''Example of distribution of one layer with 4 neurons and 3 inputs each:
        np.array([4, 3])'''
        self.number_of_neurons = distribution[0]
        self.number_of_inputs = distribution[1]
        self.synapticWeights = 2 * np.random.random((distribution[1], distribution[0])) - 1
        pass
        
class NeuralNetwork():
    def __init__(self, layerDistribution:np.array):
        '''Example of distribution array for 3 layers, fisrt one with 6 neurons and 4 inputs, second one with 2 neurons and 6 inputs and
        last one with 1 neuron and 2 inputs: np.array([[4, 6], [6, 2], [2, 1]])'''
        self.layers = np.array([])
        for distribution in layerDistribution:
            layer = NeuronLayer(distribution)
            self.layers = np.append(self.layers, layer)
        # print(self.layers)
        
    def __sigmoid(self, x):
        result = 1 / (1 + np.exp(-x))
        return(result)
    
    def __sigmoidDerivative(self, x):
        result = x * (1 - x)
        return(result)
    
    def train(self, trainingSetInputs, trainingSetOutputs, trainingIterations:int):
        counter = 10
        for iteration in range(trainingIterations):
            if iteration >= counter:
                counter += 10
                print(iteration)
            
            outputs = self.think(trainingSetInputs)

            #Calculate error, starting from the upper layer.
            #Control variable for tracking what output goes with what layer:
            adjustements = []
            for i in range(len(self.layers) - 1, -1, -1):
                #Select outputs from current layer:
                layerOutput = outputs[i]
                
                #Only in the last layer the error depends on the training output.
                if i == (len(self.layers) - 1):
                     layerError = trainingSetOutputs - layerOutput
                #In the other cases the layer error is calculated from the next layer's layerDelta and it's weights:
                else:
                    layerError = layerDelta.dot(self.layers[i+1].synapticWeights.T)
                    
                layerDelta = layerError * self.__sigmoidDerivative(layerOutput)
                
                #For adjusting the layer weights we are going to need the previous layer outputs:
                if i != 0:
                    inputs = outputs[i-1]
                else:
                    inputs = trainingSetInputs
                    rows = len(trainingSetInputs[0])
                
                #Calculate adjustement:
                layerAdjustement = inputs.T.dot(layerDelta) 
                
                adjustements.append(layerAdjustement)
                
            for i in range(len(self.layers)):
                self.layers[i].synapticWeights += adjustements[-i - 1]

     
    def checkAccuarcy(self, inputSet, outputSet):
        outputs = self.think(inputSet)[1]
        
        correctGuess = 0
        for i, output in enumerate(outputs):
            if np.argmax(output) == np.argmax(outputSet[i]):
                correctGuess += 1
        accuracy = (correctGuess / i) * 100
        return(np.mean(accuracy))
            
    def think(self, inputs):
        outputs = []
        for i, layer in enumerate(self.layers):
            if i == 0:
                output = self.__sigmoid(np.dot(inputs, layer.synapticWeights))
            #All layers except the fisrt one take as input the output of the last layer.
            else:
                output = self.__sigmoid(np.dot(output, layer.synapticWeights))
            outputs.append(output)
        # outputs = np.reshape(outputs, (len(layer.synapticWeights), len(inputs)))
        return(outputs)

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

def loadSet(id:int, version=VERSION):
    os.chdir('Sets ' + version)
    Set = np.load('Set_' + str(id) + '.npy')
    os.chdir("..")
    return(Set)

def produceSets(number:int, version=VERSION):
    os.chdir("Sets " + version)
    current_files = len(os.listdir())
    for id in range(number):
        Set = createSet()
        saveSet(Set, id + current_files)
        print(id)
    os.chdir("..")
    
def loadSets(setsSize=256, version=VERSION):
    os.chdir('Sets ' + version)
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

def saveAnalysis(analysis:np.array, id:int, version=VERSION):
    os.chdir("Analyzed " + version)
    np.save("Analyzed_" + str(id), analysis)
    os.chdir("..")

def loadAnalyzed(id:int, version=VERSION):
    os.chdir("Analyzed " + version)
    correct_output = np.load("Analyzed_" + str(id) + ".npy")
    os.chdir("..")
    return(correct_output)

def produceAnalysis(version=VERSION):
    os.chdir("Analyzed " + version)
    current_files = len(os.listdir())
    os.chdir("..")
    
    os.chdir("Sets " + version)
    number_of_sets = len(os.listdir())
    os.chdir("..")
    while current_files < number_of_sets:
        Set = loadSet(current_files, version)
        analyzed = setAnalysis(Set)
        os.chdir("Analyzed " + version)
        np.save('Analyzed_' + str(current_files), Set)
        os.chdir("..")
        current_files += 1

def loadAnalysis(version=VERSION):
    os.chdir('Analyzed ' + version)
    analysis = np.array([])
    for file in os.listdir():
        analysis = np.append(analysis, np.load(file))
    rows = int(len(analysis) / 2)
    analysis = np.reshape(analysis, (rows, 2))
    os.chdir('..')
    return(analysis)

def testNeuralNetwork(neural_network:NeuralNetwork, save=True):
    #First we load all the datasets:
    sets = loadSets(version='0.8')
    
    #After that, we divide Sets in 5 groups. To ensure that the number of sets is multiple of five
    #we discard the restant sets.
    setsSize = len(sets) - (len(sets) % DATA_SPLITTING)
    groupSize = int(setsSize / DATA_SPLITTING)
    #Control variable of number of training samples.
    training_sample_counter = 0
    error = np.array([])
    accuracy = 0
    for i in range(DATA_SPLITTING):
        print(i)
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
    
    if save:
        saveNetwork(neural_network)
        
    return(accuracy)
    
def saveNetwork(neural_network:NeuralNetwork, Id = ""):
    try:
        os.mkdir("Neural Networks " + VERSION)
        os.chdir("Neural Networks " + VERSION)
    except:
        os.chdir("Neural Networks " + VERSION)
    
    if Id != "":
        try:
            os.mkdir(Id)
            os.chdir(Id)
        except:
            os.chdir(Id)
    
    for i, layer in enumerate(neural_network.layers):
        np.save("Layer " + str(i), layer.synapticWeights)
    
    if Id != "":
        os.chdir("..")
    os.chdir("..")

def loadNetwork(Id = ""):
    os.chdir("Neural Networks " + VERSION)
    os.chdir(Id)
    
    layers = np.array([])
    for path in os.listdir():
        layer = NeuronLayer(np.array([1, 1]))
        layer.synapticWeights = np.load(path)
        layers = np.append(layers, layer)
    
    neural_network = NeuralNetwork(np.array([]))
    neural_network.layers = layers
    
    if Id != "":
        os.chdir("..")
    os.chdir("..")
    
    return(neural_network)

def create_starting_generation():
    #The first time we generate random NN:
    neural_networks = np.array([])
    for nn in range(GEN_SIZE):
        distribution = []
        number_of_layers = np.random.randint(2, 4)
        for i in range(number_of_layers):
            #layer distribution:
            #The fisrt layer has the inputs fixed:
            if i == 0:
                number_of_inputs = 3
            else:
                number_of_inputs = number_of_neurons
                
            #The last layer has the number of neurons fixed:
            if i == (number_of_layers - 1):
                number_of_neurons = 2
            else:   
                number_of_neurons = np.random.randint(1, 6)

            distribution.append([number_of_neurons, number_of_inputs])
            
        neural_network = NeuralNetwork(distribution)
        neural_networks = np.append(neural_networks, neural_network)
    return(neural_networks)

def naturalSelection():
    #Fisrt generation:
    neural_networks = create_starting_generation()
    
    #Now we have to evaluate those NN, and we are going to evaluate all at the same time 😈 Ready to burn some CPUs?
    with Pool(processes=GEN_SIZE) as pool:
        processes = []
        for i in range(GEN_SIZE):
            processes.append(pool.apply_async(testNeuralNetwork, (neural_networks[i], False)))
        accuracys = np.array([])
        for training in processes:
            accuracy = training.get()
            accuracys = np.append(accuracys, accuracy)
    print(accuracys)
        
    
if __name__ == '__main__':
    Main()