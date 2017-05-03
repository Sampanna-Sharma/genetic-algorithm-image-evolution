import os
import random

NO_OF_SPECIES = 100
NO_OF_GENE = 100



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
        self.pos = Point(random.randint(0, size[0]), random.randint(0, size[1]))
        self.color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
