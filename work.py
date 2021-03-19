

import random, copy
from music21 import converter, stream, note, chord, duration

n = 14              # number of allowed pitches, 14 is two octaves
k = 1 / 8           # shortest note length, note lengths can be a multiple of k
m = 4               # number of bars
p = 8               # pulses per bar, cannot be more than 1 / k
q = 1 / (p * k)     # one pulse has q "k's" length

# test = [ 0, 3, 6, 7, 8, 15, 15, 7, 8, 7, 6, 5, 4, 15, 15, 15, 0, 4, 5, 6, 7, 15, 15, 6, 7, 6, 5, 4, 3, 15, 15, 15 ]

ref = [ 1, 15, 1, 15, 2, 15, 3, 15,    5, 15, 5, 15, 15, 15, 15, 15,     1, 15, 3, 15, 5, 15, 3, 15,    2, 15, 4, 15, 6, 15, 4, 15 ]

def randomData(length):
    data = []
    for i in range(length):
        num = None
        while (num == None):
            num = random.randint(0, n + 1)

            if i == 0 and num == 15:
                num = None

        assert not (i == 0 and num == 15)
        data.append(num)

    return data

class DNA:
    def __init__(self, data):
        assert data[0] != 15

        self.data = copy.deepcopy(data)
        self.stream = stream.Stream()
        self.score = self.getScore(self.data)

        self.fitness = self.getFitnessScore1()
        self.selectionChance = 0



    def getM21Stream(self):
        output = stream.Stream()

        for n in self.score:
            if n[0] == 0:
                output.append(note.Rest(duration=duration.Duration(n[1] * 4)))
            else:
                output.append(note.Note(self.num_to_note_str(n[0]), duration=duration.Duration(n[1] * 4)))

        return output


    def mutate(self, eps):
        chance = random.random()
        if (chance < eps):
            index = random.randint(0, len(self.data) - 1)
            self.data[index] = random.randint(0, n + 1)

        self.fitness = self.getFitnessScore1()


    def breed(self, other, eps):
        assert len(self.data) == len(other.data)

        index = random.randint(1, len(self.data) - 2)
        child1 = DNA(self.data[:index] + other.data[index:])
        child2 = DNA(other.data[:index] + self.data[index:])

        child1.mutate(eps)
        child2.mutate(eps)

        return child1, child2


    def getFitnessScore(self):
        #fitness value calculator:
        fitnessScore = 0
        extendedNoteCount = 0
        restCount = 0
        if (self.data[0] == 0):
            restCount += 1
            fitnessScore -= 1
        for i in range(len(self.data) - 1):
            if (i % 4 == 0 and (self.data[i] == 0 or self.data[i] == 15)):    #try to have notes on beats
                fitnessScore -= 2
            if (self.data[i] != 15 and self.data[i] != 0 and self.data[i+1] != 15 and self.data[i+1] != 0):     #avoid note jumps of > 9, and approve of note jumps of <= 2
                if (abs(self.data[i] - self.data[i + 1]) < 2):
                    fitnessScore += 1
                if (abs(self.data[i] - self.data[i + 1]) > 9):
                    fitnessScore -= 1
            if (self.data[i + 1] == 0):
                restCount += 1
                if (i + 1 == len(self.data)):
                    fitnessScore -= 1
            #following statement makes extended notes follow normal rules
            if (self.data[i] != 15 and self.data[i] != 0 and self.data[i+1] == 15):    #consider note jumps across note continuations
                extendedNoteCount += 1
                temp = 1
                while ((i + temp) < len(self.data) and self.data[i + temp] == 15):    #continue until the continuation ends
                    temp += 1
                if (i + temp < len(self.data) and self.data[i + temp] != 0):     #if we didn't go over the end, and didn't follow the long note with a rest, check note jump scores
                    if (abs(self.data[i] - self.data[i + temp]) < 2):
                        fitnessScore += 1
                    if (abs(self.data[i] - self.data[i + temp]) > 9):
                        fitnessScore -= 1
            """
            #following statement makes extended notes give a bonus for *not* staying near the original note after they end
            if (self.data[i] != 15 and self.data[i] != 0 and self.data[i+1] == 15):    #consider note jumps across note continuations
                extendedNoteCount += 1
                temp = 1
                while ((i + temp) < len(self.data) and self.data[i + temp] == 15):    #continue until the continuation ends
                    temp += 1
                if (i + temp < len(self.data) and self.data[i + temp] != 0):     #if we didn't go over the end, and didn't follow the long note with a rest, check note jump scores
                    if (abs(self.data[i] - self.data[i + temp]) > 4):
                        fitnessScore += 1
            """
            """
            #alternatively, not having any additional code makes extended notes have no effect on note jump score 
            """
        if (extendedNoteCount < 3):     #if we have a very small number of extended notes, penalize the score
            fitnessScore -= (6 - (2 * extendedNoteCount)) 
        if (restCount < 3):     #if we have a very small number of rests, penalize the score
            fitnessScore -= (9 - (3 * restCount)) 
        # print("Fitness score = " + str(fitnessScore))
        # print("Fitness score = {:3}".format(fitnessScore))  #makes it so that the number lines up on the right hand side

        return (fitnessScore)


    def getFitnessScore1(self):
        assert len(self.data) == len(ref)
        
        myBars = self.bars(self.score)
        theirBars = self.bars(self.getScore(ref))

        fitness = 0
        for i in range(len(myBars)):
            rangeDiff = self.range(myBars[i]) - self.range(theirBars[i])
            fitness -= abs(rangeDiff)

            noteDiff = len(myBars[i]) - len(theirBars[i])
            fitness -= abs(noteDiff)

        return fitness
    

    @staticmethod
    def getScore(data):
        score = []

        noteNum = 0     # current note being
        noteLength = 1  # length of note in k units
        for i in range(len(data) + 1):
            cur = -1
            if (i < len(data)):
                cur = data[i]

            if i == (len(data)) or 0 <= cur <= n:
                if i > 0:
                    score.append((noteNum, noteLength * k * q))
                noteNum = cur
                noteLength = 1
            elif cur == n + 1:
                noteLength += 1

        return score


    @staticmethod
    def bars(score):
        bars = []
        fitness = 0

        for i in range(4):
            bars.append([])

        curTime = 0
        for note in score:
            index = int(curTime)
            bars[index].append(note)
            curTime += note[1]

        return bars


    @staticmethod
    def range(bar):
        max = -1000000000000000000
        min = 1000000000000000000

        for i in bar:
            cur = i[0]
            if cur < min:
                min = cur
            if cur > max:
                max = cur
        
        return max - min


    @staticmethod
    def num_to_note_str(num):
        letterAsciiOffset = ((num + 1) % 7)
        A = 65
        letter = chr(A + letterAsciiOffset)

        numberAsciiOffset = (num - 1) // 7
        _4 = 52
        number = chr(_4 + numberAsciiOffset)

        return str(letter) + str(number)


def findSelectionChance(population):
    totalFitness = 0
    lowestFitness = 1000000000000000000

    for individual in population:
        if individual.fitness < lowestFitness:
            lowestFitness = individual.fitness

    if (lowestFitness < 0) :# if the lowest fitness is negative, make it positive
        lowestFitness = -lowestFitness
    else: # otherwise we have all positive values so we don't need to do anything special
        lowestFitness = 0

    for individual in population:
        individual.fitness += lowestFitness + 1
        totalFitness += individual.fitness
    
    for individual in population:
        individual.selectionChance = individual.fitness / totalFitness
    

def select(population):
    chance = random.random()

    acc = 0
    for individual in population:
        acc += individual.selectionChance
        if chance < acc:
            return individual


def removeLeastFit(population):
    toRemove = -1
    min = 1000000000000000000

    for i in range(len(population)):
        fitness = population[i].fitness

        if (fitness < min):
            min = fitness
            toRemove = i
    
    del population[toRemove]

mutationPct = 0.05
episodes = 1000
psize = 50
population = []

for i in range(psize):
    population.append(DNA(randomData(int(m * p * q))))

for i in range(episodes):
    findSelectionChance(population)
    parent1 = select(population)
    parent2 = select(population)

    child1 = None
    child2 = None
    (child1, child2) = parent1.breed(parent2, mutationPct)
    removeLeastFit(population)
    removeLeastFit(population)

    population += [child1, child2]


max = -1000000000000000000
mostFit = None
for individual in population:
    fitness = individual.fitness
    if fitness > max:
        max = fitness
        mostFit = individual
    

stream_ = mostFit.getM21Stream()
print(stream_.timeSignature)


stream_.write('midi', 'result.mid')
