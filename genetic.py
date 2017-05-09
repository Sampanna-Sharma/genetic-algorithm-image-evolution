import os
import sys
import random
import numpy
from PIL import Image
from PIL import ImageDraw
import multiprocessing
import jsonpickle
from copy import deepcopy


POP_PER_GENERATION = 100
MUTATION_CHANCE = 0.02
ADD_GENE_CHANCE = 0.3
REM_GENE_CHANCE = 0.2
INITIAL_GENES = 200

# How often to output images and save files
GENETAIONS_PER_IMAGE = 50
GENERAIONS_PER_SAVE = 100

try:
    globalTarget = Image.open("reference.png")
except IOError:
    print("File reference.png is not present")
    exit()

# Helper Classes

class Point:
    # A 2d point
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, o):
        return Point(self.x+o.x, self.y+o.y)

class Color:
    # A color
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def shift(self, r, g, b):
        self.r = max(0, min(255, self.r+r))
        self.g = max(0, min(255, self.g+g))
        self.b = max(0, min(255, self.b+b))

    def __str__(self):
        return "({}{}{})".format(self.r, self.g, self.b)


class Gene:
    # gene
        def __init__(self, size):
            self.size = size
            self.diameter = random.randint(5, 15)
            self.pos = Point(random.randint(0, size[0]), random.randint(0, size[1]))
            self.color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.params = ["diameter", "pos", "color"]

        def mutate(self):
            mutation_size = max(1, int(round(random.gauss(15, 4))))/100
            mutation_type = random.choice(self.params)
            if mutation_type == 'diameter':
                self.diameter = random.randint(5, 15)
            elif mutation_type == 'pos':
                x = random.randint(0, self.size[0])
                y = random.randint(0, self.size[1])
                self.pos = Point(x,y)
            elif mutation_type == "color":
                self.color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        def getSave(self):
            so = {}
            so["size"] = self.size
            so["diameter"] = self.diameter
            so["pos"] = (self.pos.x, self.pos.y)
            so["color"] = (self.color.r, self.color.g, self.color.b)
            return so

        def loadSave(self, so):
            self.size = so["size"]
            self.diameter = so["diameter"]
            self.pos = Point(so["pos"][0], so["pos"][1])
            self.color = Color(so["color"][0], so["color"][1], so["color"][2])

class Organism:
    def __init__(self, size, num):
        self.size = size
        self.genes = [Gene(size) for _ in range(num)]

    def mutate(self):
        if len(self.genes) < 200:
            for g in self.genes:
                if MUTATION_CHANCE > random.random():
                    g.mutate()

        else:
            for g in random.sample(self.genes, int(len(self.genes) * MUTATION_CHANCE)):
                g.mutate()

        if ADD_GENE_CHANCE > random.random():
            self.genes.append(Gene(self.size))
        if len(self.genes) > 0 and REM_GENE_CHANCE > random.random():
            self.genes.remove(random.choice(self.genes))

    def drawImage(self):
        image = Image.new('RGB', self.size, (255, 255, 255))
        canvas = ImageDraw.Draw(image)

        for g in self.genes:
            color = (g.color.r, g.color.g, g.color.b)
            canvas.ellipse([g.pos.x-g.diameter, g.pos.y-g.diameter, g.pos.x+g.diameter, g.pos.y+g.diameter], outline = color, fill = color)
        return image

    def getSave(self, generation):
        """
        Allows us to save an individual organism in case the program is stopped.
        """
        so = [generation]
        return so + [g.getSave() for g in self.genes]

    def loadSave(self, so):
        """
        Allows us to load an individual organism in case the program is stopped.
        """
        self.genes = []
        gen = so[0]
        so = so[1:]
        for g in so:
            newGene = Gene(self.size)
            newGene.loadSave(g)
            self.genes.append(newGene)
        return gen


def fitness(im1, im2):
    i1 = numpy.array(im1, numpy.int16)
    i2 = numpy.array(im2, numpy.int16)
    dif = numpy.sum(numpy.abs(i1-i2))
    return (dif/255.0*100)/i1.size

def run(cores, so=None):
    if not os.path.exists("results"):
        os.mkdir("results")
    f = open(os.path.join("results", "log.txt"), 'a')
    target = globalTarget
    generation = 1
    parent = Organism(target.size, INITIAL_GENES)
    if so != None:
        gen = parent.loadSave(jsonpickle.decode(so))
        generation = int(gen)
    prevScore = 101
    score = fitness(parent.drawImage(), target)
    p = multiprocessing.Pool(cores)
    while True:
        print("Generation {}-{}".format(generation, score))
        f.write("Generation {}-{}/n".format(generation, score))
        if generation % GENETAIONS_PER_IMAGE == 0:
            parent.drawImage().save(os.path.join("results", "{}.png".format(generation)))
        generation += 1
        prevScore = score
        children = []
        scores = []
        children.append(parent)
        scores.append(score)

        try:
            results = groupMutate(parent, POP_PER_GENERATION-1, p)
        except KeyboardInterrupt:
            print("bye")
            p.close()
            return
        newScores, newChildren = zip(*results)

        children.extend(newChildren)
        scores.extend(newScores)

        winners = sorted(zip(children, scores), key=lambda x:x[1])
        parent, score = winners[0]

        if generation % 100 == 0:
            sf = open(os.path.join("results", "{}.txt".format(generation)), 'w')
            sf.write(jsonpickle.encode(parent.getSave(generation)))
            sf.close()

def mutateAndTest(o):
    try:
        c = deepcopy(o)
        c.mutate()
        i1 = c.drawImage()
        i2 = globalTarget
        return (fitness(i1, i2,),c)
    except KeyboardInterrupt:
        pass

def groupMutate(o, number, p):
    results = p.map(mutateAndTest, [o]*int(number))
    return results

if __name__ == "__main__":
    cores = max(1,multiprocessing.cpu_count()-1)
    so = None

    if len(sys.argv[1:]) >1:
        args = sys.argv[1:]

        for i, a in enumerate(args):
            if a == "-t":
                cores = int(args[i + 1])
            elif a == "-s":
                with open(args[i + 1], 'r') as save:
                    so = save.read()

    run(cores, so)



