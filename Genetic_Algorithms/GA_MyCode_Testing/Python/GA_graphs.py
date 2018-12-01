# pip install bitarray

import math
import random
import numpy as np
from bitarray import bitarray
import matplotlib.pyplot as plt


mutate_prob = 0.05  # Small probability with which mutation will occur.


class Population(object):
    population_list = []  # List of individuals: binary strings which represent tentative solutions.
    fitness_list = []  # List of the fitness values of each individual in the population.
    pop_size = 0  # Population Size.
    board_size = 0  # Size of problem. 'N' in N-Queen.
    pos_bits_size = 0  # Number of bits required to represent each vertical position.
    indv_size = 0  # The total size of an 'individual' binary string.

    def __init__(self, pop_size, board_size):
        self.pop_size = pop_size
        self.board_size = board_size
        self.population_list = []
        self.pos_bits_size = int(math.ceil(math.log(board_size - 1))) + 1
        self.indv_size = board_size * self.pos_bits_size

    def genPopulation(self):
        """Generates a population of bitarray strings (individuals) to solve the N-Queen problem, here N = 'board_size'.
           'pop_size' parameter decides the number of bitarray strings (individuals) generated by this function.
           Creates a list of bitarrray strings (individuals) representing the population for solving the N-Queen problem.
           'population_list' parameter holds the list of generated individuals."""
        self.population_list = []
        for i in range(0, self.pop_size):
            individual = bitarray(self.indv_size)
            # Loop for randomizing the 'individual' string.
            for j in range(0, self.board_size):
                vert_pos = random.randint(0, self.board_size - 1)
                vert_pos_bitnum = toBitArray(vert_pos, self.pos_bits_size)

                for k in range(0, self.pos_bits_size):
                    individual[j * self.pos_bits_size + k] = vert_pos_bitnum[k]
            self.population_list.append(individual)

    def computeFitnessList(self, fitnessFunction):
        """Populates the fitness list with fitness function values of co-responding entries in the population list."""
        self.fitness_list = []
        cmlsum = 0
        for individual in self.population_list:
            cmlsum = cmlsum + fitnessFunction(individual, self.board_size, self.pos_bits_size)
            self.fitness_list.append(cmlsum)

    def findInFitnessList(self, key):
        """Binary Search for finding appropriate index for key in fitness list."""
        low = 0
        high = len(self.fitness_list)
        mid = 0
        while (low <= high):
            mid = (low + high) // 2
            if key > self.fitness_list[mid]:
                low = mid + 1
            elif key < self.fitness_list[mid]:
                high = mid - 1
            else:
                break
        if low > high:
            return low
        else:
            return mid


def toBitArray(number, size):
    """Converts a number in int format to a bitarray of length 'size', in binary representation.
       Returns the bitarray."""
    temp_bitnum = bitarray(64)
    count = 0
    number = number & 0xFFFFFFFFFFFFFFFF  # enforces the number to be 64 bit.
    while count < size:
        temp_bitnum[63 - count] = (number % 2)
        # print "digit ", count, " : ", (number % 2)
        number = number >> 1
        count = count + 1
    return temp_bitnum[-size:]


def fromBitArray(bitnum):
    """Converts a bitarray in binary format to a number in int format, to its co-responding decimal representation.
       Returns the number."""
    number = 0 & 0xFFFFFFFFFFFFFFFF  # enforces the number to be 64 bit.
    idx = len(bitnum) - 1
    number = number + bitnum[idx]
    idx = idx - 1
    count = 1
    while idx != -1:
        number = number + (bitnum[idx] << count)
        count = count + 1
        idx = idx - 1
    return number


def fitnessFunction(individual, board_size, pos_bits_size):
    """Calculates the finess value of an individual and returns it.
       Has a computational complexity of O(1) per piece."""
    right_diag = [0] * (2 * board_size - 1)
    left_diag = [0] * (2 * board_size - 1)
    vertical = [0] * board_size
    conflicts = 0
    idx = 0
    while idx < board_size:
        # print "idx: ",idx,individual[idx * pos_bits_size : idx * pos_bits_size + pos_bits_size]
        vpos = fromBitArray(individual[idx * pos_bits_size: idx * pos_bits_size + pos_bits_size])
        # print "vpos: ", vpos + 1
        if vertical[vpos] != 0:
            conflicts = conflicts + vertical[vpos]
        vertical[vpos] = vertical[vpos] + 1
        if left_diag[vpos + idx] != 0:
            conflicts = conflicts + left_diag[vpos + idx]
        left_diag[vpos + idx] = left_diag[vpos + idx] + 1
        if right_diag[vpos + board_size - idx - 1] != 0:
            conflicts = conflicts + right_diag[vpos + board_size - idx - 1]
        right_diag[vpos + board_size - idx - 1] = right_diag[vpos + board_size - idx - 1] + 1
        idx = idx + 1
    return (board_size * (board_size - 1)) / 2 - conflicts


def geneticAlgorithm(population, fitnessFunction):
    global mutate_prob
    child = None
    condition = True
    while condition:
        population.computeFitnessList(fitnessFunction)
        new_pop = []
        for i in range(0, len(population.population_list)):
            parent_x = None
            parent_y = None
            (parent_x, parent_y) = randomSelection(population)
            child = reproduce(parent_x, parent_y, population)
            if mutate_prob > random.random():
                mutate(child, population)
            new_pop.append(child)
        population.population_list = new_pop
        condition = (fitnessFunction(child, population.board_size, population.pos_bits_size) != (population.board_size * (population.board_size - 1)) / 2)
        # check condition
    return child


def randomSelection(population):
    rand_sel_x = random.randint(1, population.fitness_list[len(population.fitness_list) - 1])
    parent_x_idx = population.findInFitnessList(rand_sel_x)
    range_rem = population.fitness_list[parent_x_idx]
    if rand_sel_x > population.fitness_list[0]:
        range_rem = range_rem - population.fitness_list[parent_x_idx - 1]
    rand_sel_y = random.randint(1, population.fitness_list[len(population.fitness_list) - 1] - range_rem)
    if rand_sel_y >= rand_sel_x:
        rand_sel_y = rand_sel_y + range_rem
    parent_y_idx = population.findInFitnessList(rand_sel_y)
    parent_x = population.population_list[parent_x_idx]
    parent_y = population.population_list[parent_y_idx]
    return (parent_x, parent_y)


def reproduce(parent_x, parent_y, population):
    crossover_pt = random.randint(1, population.board_size - 1)
    # print crossover_pt
    return parent_x[:crossover_pt * population.pos_bits_size] + parent_y[crossover_pt * population.pos_bits_size:]


def mutate(child, population):
    rand_idx = random.randint(0, population.board_size - 1)
    rand_vpos = random.randint(0, population.board_size - 1)
    temp_bitnum = toBitArray(rand_vpos, population.pos_bits_size)
    # print "mutate: ", rand_idx, temp_bitnum
    for i in range(0, population.pos_bits_size):
        child[rand_idx * population.pos_bits_size + i] = temp_bitnum[i]


def main(pop_size):
    new_pop = Population(pop_size, 8)
    new_pop.genPopulation()
    result = geneticAlgorithm(new_pop, fitnessFunction)

    print("fitness length: {}".format(len(new_pop.fitness_list)))
    print("final result: \t")
    for i in range(0, new_pop.board_size):
        print(fromBitArray(result[i * new_pop.pos_bits_size: i * new_pop.pos_bits_size + new_pop.pos_bits_size]) + 1, end=' ')

    axis = range(0, pop_size, 1)
    plt.axis([axis[0], axis[-1], 0, 1])
    plt.plot(axis, np.array(new_pop.fitness_list)/np.array(new_pop.fitness_list).max())
    plt.title("fitness vs generation")
    plt.show()


if __name__ == "__main__":
    main(100)
