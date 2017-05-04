import os
import random
from PIL import Image
from PIL import ImageDraw
import numpy
import multiprocessing
from copy import deepcopy


NO_OF_SPECIES = 100
NO_OF_GENE = 100
MUTATION_CHANCE = 0.02


#Checking if the image file exists or not
try:
    globalTarget = Image.open("reference.png")
except IOError:
    print("There is no reference.png file in the directory")
    exit()





class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class Gene:
    def __init__(self, size):
        self.size = size
        self.diameter = random.randint(2, 15)
        self.pos = Point(random.randint(0, self.size[0]), random.randint(0, self.size[1]))
        self.color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.paras = ['diameter', 'position', 'color']

    def mutate(self):
        mutate_type = random.choice(self.paras)

        if mutate_type == 'diameter':
            self.diameter = random.randint(2, 15)
        elif mutate_type == 'position':
            self.pos = Point(random.randint(0, self.size[0]), random.randint(0, self.size[1]))
        elif mutate_type == 'color':
            self.color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


class Organism:
    def __init__(self, size):
        self.size = size
        self.organism = [Gene(self.size) for _ in range(NO_OF_GENE)]

    def mutate(self):
        for g in self.organism:
            if MUTATION_CHANCE > random.random():
                g.mutate()

    def draw_image(self):
        image = Image.new("RGB", self.size, (255, 255, 255))
        canvas = ImageDraw.Draw(image, 'RGB')
        for g in self.organism:
            color = (g.color.r, g.color.g, g.color.b)
            canvas.ellipse([g.pos.x - g.diameter, g.pos.y - g.diameter, g.pos.x + g.diameter, g.pos.y + g.diameter],
                           outline=color, fill=color)
            return image


def calcfitness(i1, i2):
    p1 = numpy.array(i1, numpy.int16)
    p2 = numpy.array(i2, numpy.int16)
    dif = numpy.sum(numpy.abs(p1-p2))
    fitness = ((dif/255.0)*100)/p1.size
    return fitness


def run():
    if not os.path.exists('results'):
        os.mkdir('results')

    fp = open(os.path.join('results', 'log.txt'), 'a')
    target = globalTarget

    generation = 1

    parent = Organism(target.size)
    score = calcfitness(parent.draw_image(), target)

    p = multiprocessing.Pool(2)

    while True:
        print("Genreation {}- {}".format(generation, score))
        fp.write("Genreation {}- {}".format(generation, score))
        if generation % 50 is 0:
            parent.draw_image().save(os.path.join('results', '{}.png'.format(generation)))
        generation += 1
        children = []
        scores = []
        children.append(parent)
        scores.append(score)
        try:
            result = groupmutate(parent, NO_OF_SPECIES-1, p)
        except KeyboardInterrupt:
            print("bye")
            p.close()
            return
        newscore, newchild = zip(*result)
        children.extend(newchild)
        scores.extend(newscore)
        winner = sorted(zip(children, scores), key=lambda x: x[1])
        parent, score = winner[0]




def mutateandgo(o):
    try:
        c = deepcopy(o)
        c.mutate()
        i1 = c.draw_image()
        i2 = globalTarget
        return calcfitness(i1, i2, ), c
    except KeyboardInterrupt:
        pass


def groupmutate(o, number, p):
    results = p.map(mutateandgo, [o]*int(number))
    #results = [mutateandgo(i) for i in [o]*int(number)]
    return results

if __name__ == '__main__':
    run()








