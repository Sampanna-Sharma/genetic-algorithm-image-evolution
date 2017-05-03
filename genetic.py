import os
import random
from PIL import Image
from PIL import ImageDraw

NO_OF_SPECIES = 100
NO_OF_GENE = 100


#Checking if the image file exists or not
try :
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
        self.paras = {'diameter', 'position', 'color'}

    def mutate(self):
        mutate_type = random.choice(self.paras)

        if mutate_type == 'diameter':
            self.diameter = random.randint(2, 15)
        elif mutate_type == 'position':
            self.pos = Point(random.randint(0, self.size[0]), random.randint(0, self.size[1]))
        elif mutate_type == 'color':
            self.color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class Organism:
    def __index__(self, size):
        self.size = size
        self.organism = [Gene(self.size) for _ in range(NO_OF_GENE)]





