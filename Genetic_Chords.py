
# -*- coding: utf-8 -*-

# Casos de prueba:
# 2# 54 67 69 61 62
# 1# 43 50 48 47 45 43 55 52 50 48 52 50 50 43 45 47 48 47 48 52 50 38 43
# 2# 50 43 49 50 52 45 49 50 43 45 50
# 2b 46 50 48 51 53 51 48 45 46


import random
import math
import numpy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

"""
si la armadura tiene # se multiplica 7 por el número de sostenidos mod(12)
si la armadura tiene b se multiplica 5 por el número de bemoles mod(12)
"""

# Global Variables
OPTIONS_M = ((0, -3, 5),
             (0, -3, 5),
             (0, -4, 5),
             (0, -3, 6),
             (0, -3, 5),
             (0, -4, 5),
             (0, -4, 5)
            )
OPTIONS_m = ((0, -4, 5),
             (0, -4, 5),
             (0, -3, 5),
             (0, -3, 5),
             (0, -4, 5),
             (0, -3, 6),
             (0, 5)
            )
MOD_M = ('M', 'm', 'm', 'M', 'M', 'm', 'd')
MOD_m = ('m', 'd', 'M', 'm', 'M', 'M', 'M')


def neighborhood(iterable):
    """Generator gives the prev actual and next"""
    iterator = iter(iterable)
    prev = None
    item = next(iterator)  # throws StopIteration if empty.
    for nex in iterator:
        yield (prev, item, nex)
        prev = item
        item = nex
    yield (prev, item, None)


def setTon(line):
    """Determine the tonality of the exercice"""
    ton = line[:2]
    notes = list(map(int, line[3:].split(' ')))
    if ton[1] == '#':
        ton = (int(ton[0]) * 7) % 12
    else:
        ton = (int(ton[0]) * 5) % 12
    for note in notes:
        if (ton + 6) % 12 == note % 12:
            ton = str((ton - 3) % 12) + 'm'
            break
    else:
        if ton - 3 == notes[-1] % 12:
            ton = str((ton - 3) % 12) + 'm'
        else:
            ton = str(ton) + 'M'
    return ton, notes


def creatChord(nameC, noteF):
    """Create one chord given the name of the chord and the fundamental note"""
    num_funda = int(nameC[:-1])
    if nameC[-1] == 'M':
        val_notes = [num_funda, (num_funda + 4) % 12, (num_funda + 7) % 12]
    elif nameC[-1] == 'm':
        val_notes = [num_funda, (num_funda + 3) % 12, (num_funda + 7) % 12]
    elif nameC[-1] == 'd':
        val_notes = [num_funda, (num_funda + 3) % 12, (num_funda + 6) % 12]

    tenorR = list(range(48, 69))
    contR = list(range(52, 77))
    sopR = list(range(60, 86))

    # Depending in the bass note this are the options for the others voices
    if noteF % 12 == val_notes[0]:
        opc = [[1, 1, 1], [2, 1, 0], [0, 1, 2]]
    elif noteF % 12 == val_notes[1]:
        opc = [[1, 0, 2], [3, 0, 0], [2, 0, 1]]
    elif noteF % 12 == val_notes[2]:
        opc = [[1, 1, 1], [2, 1, 0]]

    opc = random.choice(opc)
    chordN = list()
    for num, val in zip(opc, val_notes):
        chordN += [val] * num

    random.shuffle(chordN)

    chord = [noteF, ]
    for nte, voce in zip(chordN, [tenorR, contR, sopR]):
        posible_n = [x for x in voce if x % 12 == nte]
        chord.append(random.choice(posible_n))

    return chord


def selChord(ton, notesBass):
    """Select the chords from all the posibilities"""
    listaOp = OPTIONS_M if ton[-1] == 'M' else OPTIONS_m
    listaMod = MOD_M if ton[-1] == 'M' else MOD_m
    prog = list()

    for note in notesBass:
        name = note % 12
        grad = name - int(ton[:-1])
        grad = math.ceil(((grad + 12) % 12) / 2)
        num = (listaOp[grad][random.randint(0, len(listaOp[grad]) - 1)]
               + name + 12) % 12
        grad = num - int(ton[:-1])
        grad = math.ceil(((grad + 12) % 12) / 2)
        name = '{}{}'.format(num, listaMod[grad])
        prog.append([creatChord(name, note), grad])
    return prog


def newChordProg(ton, notes):
    """Create a new individual given the tonality and the base notes"""
    chords = selChord(ton, notes)
    for c in chords:
        yield c


def check_interval(chord):
    """Return the number of mistakes in the distance between the notes"""
    res = 0
    if chord[2] - chord[1] > 12 or chord[2] - chord[1] < 0:
        res += 15
    if chord[3] - chord[2] > 12 or chord[3] - chord[2] < 0:
        res += 15

    if chord[1] == chord[2] or chord[2] == chord[3]:
        res += 1.4
    return res


def check_2_chords(ch1, ch2):
    """Return the number of mistakes in the intervals between 2 chords"""
    res = 0

    # Check for 5° and 8°
    ite1 = map(lambda x, y: y - x, ch1[:-1], ch1[1:])
    ite2 = map(lambda x, y: y - x, ch2[:-1], ch2[1:])
    for inter1, inter2 in zip(ite1, ite2):
        if inter1 == 7 and inter2 == 7:
            res += 15
        elif inter1 == 0 and inter2 == 0:
            res += 15
        elif inter1 == 12 and inter2 == 12:
            res += 15

    # Check for big intervals, just to make it more "human"
    for note1, note2 in zip(ch1[1:], ch2[1:]):
        if abs(note1 - note2) >= 7:  # 7 equals 5° interval
            res += .7

    return res


def evalNumErr(ton, individual):
    """Evaluation function"""
    res = 0
    for prev, item, nex in neighborhood(individual):
        res += check_interval(item[0])
        if prev is None:
            if item[1] != 0:
                res += 6
            continue
        else:
            if prev[1] in [4, 6] and item[1] in [3, 1]:
                res += 20
            res += check_2_chords(prev[0], item[0])
        if nex is None:
            if item[1] in [1, 2, 3, 4, 5, 6]:
                res += 6
    return (res,)


def mutChangeNotes(ton, individual, indpb):
    """Mutant function"""
    new_ind = toolbox.clone(individual)
    for x in range(len(individual[0])):
        if random.random() < indpb:

            listaOp = OPTIONS_M if ton[-1] == 'M' else OPTIONS_m
            listaMod = MOD_M if ton[-1] == 'M' else MOD_m

            note = individual[x][0][0]

            name = note % 12
            grad = name - int(ton[:-1])
            grad = math.ceil(((grad + 12) % 12) / 2)
            num = (listaOp[grad][random.randint(0, len(listaOp[grad]) - 1)]
                   + name + 12) % 12
            grad = num - int(ton[:-1])
            grad = math.ceil(((grad + 12) % 12) / 2)
            name = '{}{}'.format(num, listaMod[grad])

            new_ind[x] = [creatChord(name, note), grad]

    del new_ind.fitness.values
    return new_ind,


def transform_lilypond(ton, indiv):
    """Take one list of chords and print the it in lilypond notation"""
    note_map = dict()
    if ton[-1] == 'M':
        note_map = {0: 'c',
                    1: 'cis',
                    2: 'd',
                    3: 'dis',
                    4: 'e',
                    5: 'f',
                    6: 'fis',
                    7: 'g',
                    8: 'gis',
                    9: 'a',
                    10: 'ais',
                    11: 'b'
                    }
    else:
        note_map = {0: 'c',
                    1: 'des',
                    2: 'd',
                    3: 'ees',
                    4: 'e',
                    5: 'f',
                    6: 'ges',
                    7: 'g',
                    8: 'aes',
                    9: 'a',
                    10: 'bes',
                    11: 'b'
                    }
    voces = [[], [], [], []]

    for chord in indiv:
        for note, voce in zip(chord, voces):

            octave = (note // 12) - 4
            name_lily = note_map[note % 12]
            if octave < 0:
                name_lily += ',' * (octave * -1)
            elif octave > 0:
                name_lily += "'" * octave
            voce.append(name_lily)
    form_txt = '{}|\n{}|\n{}|\n{}|\n'
    print(form_txt.format(*(' '.join(voce) for voce in reversed(voces))))


def main(ton):
    pop = toolbox.population(n=400)
    hof = tools.HallOfFame(3)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register('avg', numpy.mean)
    stats.register('std', numpy.std)
    stats.register('min', numpy.min)
    stats.register('max', numpy.max)

    pop, log = algorithms.eaSimple(pop,
                                   toolbox,
                                   cxpb=0.5,
                                   mutpb=0.3,
                                   ngen=70,
                                   stats=stats,
                                   halloffame=hof,
                                   verbose=True)
    while min(log.select('min')) > 15:
        pop = toolbox.population(n=400)
        pop, log = algorithms.eaSimple(pop,
                                       toolbox,
                                       cxpb=0.5,
                                       mutpb=0.3,
                                       ngen=70,
                                       stats=stats,
                                       halloffame=hof,
                                       verbose=True)

    for best in hof:
        print([x[0] for x in best])

        transform_lilypond(ton, [x[0] for x in best])


if __name__ == '__main__':
    line = input('n[#b] notas ')
    ton, notes = setTon(line)
    print(ton, notes)

    # ========================= GA setup =========================
    creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register('creat_notes', newChordProg, ton, notes)
    toolbox.register('individual', tools.initIterate, creator.Individual,
                     toolbox.creat_notes)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)

    toolbox.register('evaluate', evalNumErr, ton)
    toolbox.register('mate', tools.cxOnePoint)
    toolbox.register('mutate', mutChangeNotes, ton, indpb=0.4)
    toolbox.register('select', tools.selTournament, tournsize=3)
    # =============================================================

    main(ton)

    """
    a = toolbox.individual()
    transform_lilypond(x[0] for x in a)


    print(toolbox.evaluate(a))
    b = toolbox.individual()
    print(b)
    print(toolbox.evaluate(b))
    a,b = toolbox.mate(a,b)
    print(a)
    print(b)
    print("_"*20)

    a = toolbox.mutate(a)
    print(a)
    print("-"*20)
    """


# ---Code for transform human chords to lilypond notation---
"""
human1 = [[43, 55, 62, 71],
         [50, 54, 62, 69],
         [48, 55, 64, 72],
         [47, 55, 66, 74],

         [45, 57, 64, 72],
         [43, 59, 67, 74],
         [55, 60, 64, 72],
         [52, 60, 67, 72],

         [50, 62, 66, 74],
         [48, 64, 69, 76],
         [52, 64, 67, 71],
         [50, 57, 66, 69],

         [50, 54, 62, 69],
         [43, 55, 62, 71],
         [45, 52, 64, 72],
         [47, 55, 62, 67],

         [48, 55, 64, 72],
         [47, 55, 62, 71],
         [48, 55, 64, 67],
         [52, 55, 64, 71],

         [50, 57, 66, 74],
         [38, 50, 62, 66],
         [43, 55, 62, 67]
         ]
transform_lilypond(human1)

human2 = [[50, 57, 66, 74],
          [43, 59, 67, 74],
          [49, 57, 64, 69],
          [50, 57, 66, 69],

          [52, 55, 64, 71],
          [45, 57, 64, 73],
          [49, 55, 64, 73],
          [50, 54, 62, 69],

          [43, 55, 62, 71],
          [45, 52, 61, 69],
          [50, 54, 62, 69]
          ]
transform_lilypond(human2)

human3 = [[46, 53, 62, 70],
          [50, 53, 62, 69],
          [48, 55, 63, 72],
          [51, 55, 63, 70],

          [53, 57, 62, 74],
          [51, 58, 67, 75],
          [48, 57, 65, 77],
          [45, 57, 63, 72],

          [46, 53, 62, 70]
          ]
transform_lilypond(human3)

"""
#### Buenos resultados:

##BASE 1# 43 50 48 47 45 43 55 52 50 48 52 50 50 43 45 47 48 47 48 52 50 38 43
"""
PRIMERA GENERACIÓN
d' g' e'' b' d'' b' d'' e'' b' a'' c'' g' b' e' a' g' fis'' d' a' c'' b' d' g''|
d' d' e' b' d' g' d' g' g' a' e' b b b c' g' a' g a' c' g' a g'|
b b a d' fis d' b b g' a a d fis b a g c' d a g g' fis b|
g, d c b, a, g, g e d c e d d g, a, b, c b, c e d d, g,|

SEGUNDA GENERACIÓN
d'' a' fis' g' c' e' d' b' b' a' c''' d'' d'' e' e' g' fis'' d'' a'' e'' a' b' g'|
d' d' a d' a b b g' b' a' c'' g' fis' b c' e' a' g' a' g' d' fis' b|
b fis fis d e e g b b e' c' b a b e b fis' d' a b fis fis g|
g, d c b, a, g, g e d c e d d g, a, b, c b, c e d d, g,|

g' d' fis' b' fis' g' b' a' b' e'' a'' fis'' fis' e'' d'' b' fis'' b' g' b' g'' d'' d''|
b fis a d' c' d' e' c' b' c'' c'' fis' d' e' fis' d' fis' d' g' g' g' g' d'|
g d fis b fis b b a b g' e' b a e d' b a b e' b b b b|
g, d c b, a, g, g e d c e d d g, a, b, c b, c e d d, g,|

g' b' fis' b' fis' g' b' a' b' e'' a'' fis'' fis' e'' d'' b' fis'' b' g' b' g'' d'' d''|
b d' a d' c' d' e' c' b' c'' c'' fis' d' e' fis' d' fis' d' g' g' g' g' d'|
g g fis b fis b b a b g' e' b a e d' b a b e' b b b b|
g, d c b, a, g, g e d c e d d g, a, b, c b, c e d d, g,|

b' fis' a' fis' c'' b' g' g' fis'' a'' g'' fis'' b' c'' a' g' a' b' a' e'' a' d'' g'|
d' b e' fis' a' d' d' b b' c'' b' b' b g' c' g' e' d' a' a' fis' g' b|
d fis e d' a d' b e fis' fis' e' b b e' a g' e fis a c' a b g|
g, d c b, a, g, g e d c e d d g, a, b, c b, c e d d, g,|

TERCERA

# good
d'' d'' c'' e'' c'' d' e' c'' b' a'' e'' b'' a' b'' fis'' e'' a'' g'' e'' e'' g'' a' g''|
g' fis' fis' e' fis' b c' c' fis' a' g' b' fis' e'' c'' b' c'' d'' a' g' g' fis' b'|
b a a g fis d g c' b a b b d' e' fis' g' fis' g' a b b a g'|
g, d c b, a, g, g e d c e d d g, a, b, c b, c e d d, g,|

g' d' e' e' fis' e'' c'' a' b' a'' c'' b' fis'' g'' a' b' fis' fis' a' g' b' b' d''|
b b g b fis' e' e' c' fis' a' e' g' a' g' fis' d' c' d' c' b fis' g' d'|
g g g g fis b c' a b a a d' a b d' b a b fis b b d' b|
g, d c b, a, g, g e d c e d d g, a, b, c b, c e d d, g,|


2# 50 43 49 50 52 45 49 50 43 45 50

d'' b' a' g' a' fis' cis' fis' g' cis' d''|
fis' e' cis' d' cis' cis' a a cis' a d'|
a e fis b a fis fis d e a fis|
d g, cis d e a, cis d g, a, d|

d'' g'' a'' fis'' cis'' e'' cis'' d'' d'' d'' fis''|
a' cis'' a' b' g' cis'' a' fis' d' fis' a'|
fis' e' e' fis' cis' e' fis' d' b d' a|
d g, cis d e a, cis d g, a, d|

# good
d' cis' fis' b' a' a' g' fis' e' d' fis'|
fis g a d' cis' cis' e' d' cis' a d'|
d e cis g a a g a g fis d|
d g, cis d e a, cis d g, a, d|

# good
fis'' e'' e'' b' a' a' fis' fis' e' d' fis'|
a' e' a' fis' cis' cis' a b cis' a d'|
a b e' b a a fis fis g fis d|
d g, cis d e a, cis d g, a, d|

# very good
a' g' a' a' a' a' fis' b' b' a' d''|
fis' d' fis' fis' cis' cis' cis' g' e' e' fis'|
a b cis' a a a a g b cis' d'|
d g, cis d e a, cis d g, a, d|


2b 46 50 48 51 53 51 48 45 46

d'' bes' ees'' c'' d'' g'' f'' f'' d''|
f' f' g' ees' d' bes' a' a' bes'|
f bes g a a ees' f' d' bes|
bes, d c ees f ees c a, bes,|
"""