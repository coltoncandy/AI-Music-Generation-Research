# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# <a href="https://colab.research.google.com/github/coltoncandy/AI-Music-Generation-Research/blob/main/Genetic_Music_Generator.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %%
# from google.colab import drive
# drive.mount('/content/gdrive', force_remount=True)
# PROJECT_PATH = "/content/gdrive/Shareddrives/AI Winter 2021 Group Project/Genetic Algorithm 1.0.0"

# %%

import random
from music21 import converter, stream, note, chord, duration

'''
1   ->  C4
2   ->  D4
3   ->  E4
4   ->  F4
5   ->  G4
6   ->  A4
7   ->  B4

8   ->  C5
9   ->  D5
10  ->  E5
11  ->  F5
12  ->  G5
13  ->  A5
14  ->  B5
'''
def num_to_note_str(num):
    # convert num from 1-14 to 0-6, so mod 7 
    # however, after that C=1, A=6, B=0
    # We want : A=0, B=1, C=2, etc
    # So, add 1 and mod 7
    letterAsciiOffset = ((num + 1) % 7)
    A = 65
    letter = chr(A + letterAsciiOffset)

    numberAsciiOffset = (num - 1) // 7
    _4 = 52
    number = chr(_4 + numberAsciiOffset)

    return str(letter) + str(number)

n = 14              # number of allowed pitches
k = 1 / 8           # shortest duration
m = 4               # number of bars
p = 8               # pulses per bar, cannot be more than 1 / k
q = 1 / (p * k)     # one pulse has q shortest lengths

# search space is (n + 2)^(m * p * q)
# for 4 bars, and p = 8 , then the search space is 3.4 x 10^38

# each value is in the range [0,n+1]
# each value by default has k note length
# if dna[i] = 0 then it is a break
# if 1 <= dna[i] <= n, then it is a midi note in the range [R,n-1] where R is the reference note
# if dna[i] = n + 1, then the previous note is lengthened by k
#   i.e. to make a note last t*k duration, repeat n + 1 t times
dna = []

print(m * p * q)
for i in range(0, int(m * p * q)):
    dna.append(random.randint(0, n + 1))

dna = [ 0, 3, 6, 7, 8, 15, 15, 7, 8, 7, 6, 5, 4, 15, 15, 15, 0, 4, 5, 6, 7, 15, 15, 6, 7, 6, 5, 4, 3, 15, 15, 15 ]

# intermediate between msuci21 stream and dna
# almost the same as dna, except that repeating n+1s are collapsed
# into note length
# score = [(note, length)] where 0 <= note <= n (0 is still a rest), length is in seconds
score = []

noteNum = 0     # current note being
noteLength = 1  # length of note in k units

for i in range(0, len(dna) + 1):
    cur = -1
    if (i < len(dna)):
        cur = dna[i]

    if i == (len(dna)) or 0 <= cur <= n:
        if i > 0:
            score.append((noteNum, noteLength * k * q))
        noteNum = cur
        noteLength = 1
    elif cur == n + 1:
        noteLength += 1

output = stream.Stream()

for n in score:
    if n[0] == 0:
        output.append(note.Rest(duration=duration.Duration(n[1] * 4)))
    else:
        output.append(note.Note(num_to_note_str(n[0]), duration=duration.Duration(n[1] * 4)))

for n in output.flat.elements:
    print(str(n) + ' ' + str(n.duration))

output.write('midi', 'test.mid')