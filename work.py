

import random, copy
from music21 import converter, stream, note, chord, duration

n = 14              # number of allowed pitches, 14 is two octaves
k = 1 / 8           # shortest note length, note lengths can be a multiple of k
m = 4               # number of bars
p = 8               # pulses per bar, cannot be more than 1 / k
q = 1 / (p * k)     # one pulse has q "k's" length

# test = [ 0, 3, 6, 7, 8, 15, 15, 7, 8, 7, 6, 5, 4, 15, 15, 15, 0, 4, 5, 6, 7, 15, 15, 6, 7, 6, 5, 4, 3, 15, 15, 15 ]

def randomData(m, p, q):
    data = []
    for i in range(0, int(m * p * q)):
        data.append(random.randint(0, n + 1))

    return data

class DNA:
    def __init__(self, data):
        self.data = copy.deepcopy(data)
        self.stream = stream.Stream()

        self.getScore()


    def getScore(self):
        self.score = []

        noteNum = 0     # current note being
        noteLength = 1  # length of note in k units
        for i in range(0, len(self.data) + 1):
            cur = -1
            if (i < len(self.data)):
                cur = self.data[i]

            if i == (len(self.data)) or 0 <= cur <= n:
                if i > 0:
                    self.score.append((noteNum, noteLength * k * q))
                noteNum = cur
                noteLength = 1
            elif cur == n + 1:
                noteLength += 1

    def num_to_note_str(num):
        letterAsciiOffset = ((num + 1) % 7)
        A = 65
        letter = chr(A + letterAsciiOffset)

        numberAsciiOffset = (num - 1) // 7
        _4 = 52
        number = chr(_4 + numberAsciiOffset)

        return str(letter) + str(number)


    def getM21Stream(self):
        output = stream.Stream()

        for n in self.score:
            if n[0] == 0:
                output.append(note.Rest(duration=duration.Duration(n[1] * 4)))
            else:
                output.append(note.Note(num_to_note_str(n[0]), duration=duration.Duration(n[1] * 4)))

        return output


    def mutate(self, eps):
        chance = random.random()
        if (chance < eps):
            index = random.randint(0, len(self.data) - 1)
            self.data[index] = randint(0, n + 1)


    def breed(self, other, eps):
        assert len(self.data) == len(other.data)

        index = random.randint(1, len(self.data) - 2)
        child1 = DNA(self.data[:index] + other.data[index:])
        child2 = DNA(other.data[:index] + self.data[index:])

        child1.mutate(eps)
        child2.mutate(eps)

        return child1, child2


dna = DNA(randomData(m, p, q))
dna.getM21Stream().write('midi', 'test.mid')
