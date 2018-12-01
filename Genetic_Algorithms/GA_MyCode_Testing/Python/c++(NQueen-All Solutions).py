import numpy as np
import os
import sys
import random
import matplotlib.pyplot as plt
import time

N = 10
xdata = []
ydata = []
plt.show()
axes = plt.gca()
axes.set_xlim(0, 1000)
axes.set_ylim(0, 40)
line, = axes.plot(xdata, ydata, 'r-')

csv_x_index = 0

if os.path.exists('graph.csv'):
    os.remove('graph.csv')

def draw_plot(data):
    if len(xdata) >= 1000:
        xdata.clear()
        ydata.clear()
    xdata.append(len(xdata))
    ydata.append(data)
    line.set_xdata(xdata)
    line.set_ydata(ydata)
    plt.xlabel("generation")
    plt.ylabel("cost value")
    plt.title("cost per each generation")
    plt.draw()

    # write to csv file
    with open("graph.csv", "a") as graph:
        global csv_x_index
        graph.write("{},{}\n".format(csv_x_index+1, data))
        csv_x_index += 1
        graph.close()

    plt.pause(1e-17)


class GAQueen:
    def __init__(self, population, iteration, mutation):
        self.population = population
        self.iteration = iteration
        self.mutation = mutation
        self.boardlength = N
        self.chromosome_matrix = np.zeros((30, 1000))
        self.cost_matrix = np.zeros(1000)
        self.crossovermatrix = np.zeros((30, 1000))
        self.area = np.zeros((30, 30))
        self.solutions = 0

    def clear(self):
        self.area = np.zeros((30, 30))

    def find_solution(self):
        positions = [-1] * self.boardlength
        self.put_queen(positions, 0)
        print("Number of total solutions: {}".format(self.solutions))

    def put_queen(self, positions, target_row):
        """
        Try to place a queen on target_row by checking all N possible cases.
        If a valid place is found the function calls itself trying to place a queen
        on the next row until all N queens are placed on the NxN board.
        """
        # Base (stop) case - all N rows are occupied
        if target_row == self.boardlength:
            # self.show_full_board(positions)
            self.show_short_board(positions)
            self.solutions += 1
        else:
            # For all N columns positions try to place a queen
            for column in range(self.boardlength):
                # Reject all invalid positions
                if self.check_place(positions, target_row, column):
                    positions[target_row] = column
                    self.put_queen(positions, target_row + 1)

    def check_place(self, positions, ocuppied_rows, column):
        """
        Check if a given position is under attack from any of
        the previously placed queens (check column and diagonal positions)
        """
        for i in range(ocuppied_rows):
            if positions[i] == column or positions[i] - i == column - ocuppied_rows or positions[i] + i == column + ocuppied_rows:
                return False
        return True

    def show_short_board(self, positions):
        """
        Show the queens positions on the board in compressed form,
        each number represent the occupied column position in the corresponding row.
        """
        line = "_".join(str(positions[i]) for i in range(self.boardlength))
       
        """
        print(line)
        """
        with open("final.csv", "a") as result:
            result.write(line + "\n")
            result.close()

    def cost_func(self, idx):
        cost_value = 0
        for i in range(self.boardlength):
            j = int(self.chromosome_matrix[i][idx])
            m = i + 1
            n = j - 1
            while m < self.boardlength and n >= 0:
                if int(self.area[m][n]) == 1:
                    cost_value += 1  # there is a queen that takes the other one
                m += 1
                n -= 1

            m = i + 1
            n = j + 1
            while m < self.boardlength and n < self.boardlength:
                if int(self.area[m][n]) == 1:
                    cost_value += 1
                m += 1
                n += 1

            m = i - 1
            n = j - 1
            while m >= 0 and n >= 0:
                if int(self.area[m][n]) == 1:
                    cost_value += 1
                m -= 1
                n -= 1

            m = i - 1
            n = j + 1
            while m >= 0 and n < self.boardlength:
                if int(self.area[m][n]) == 1:
                    cost_value += 1
                m -= 1
                n += 1

        return cost_value

    def initial_population(self):
        rand = 0
        check = False
        for index in range(self.population):
            a = 0
            while a < self.boardlength:
                rand = random.randrange(32768)
                check = 1
                for b in range(a):
                    if rand % self.boardlength == int(self.chromosome_matrix[b][index]):
                        check = 0
                if check:
                    self.chromosome_matrix[a][index] = rand % self.boardlength
                else:
                    a -= 1
                a += 1

    def population_sort(self):
        k = 1
        while k:
            k = 0
            for i in range(self.population-1):
                if int(self.cost_matrix[i]) > int(self.cost_matrix[i+1]):
                    temp = int(self.cost_matrix[i])
                    self.cost_matrix[i] = int(self.cost_matrix[i+1])
                    self.cost_matrix[i+1] = temp

                    for j in range(self.boardlength):
                        temp = int(self.chromosome_matrix[j][i])
                        self.chromosome_matrix[j][i] = int(self.chromosome_matrix[j][i+1])
                        self.chromosome_matrix[j][i+1] = temp

                    k = 1

    def mating(self):
        temp_matrix = np.zeros((self.boardlength, 2))
        temp_matrix0 = np.zeros(self.boardlength)
        temp_matrix1 = np.zeros(self.boardlength)

        for index in range(self.population//4):
            for t in range(2):
                for i in range(self.boardlength):
                    temp_matrix0[i] = int(self.chromosome_matrix[i][2 * index])
                    temp_matrix1[i] = int(self.chromosome_matrix[i][2 * index + 1])

                for i in range(self.boardlength):
                    if int(self.crossovermatrix[i][2*index+t]) == 0:
                        for j in range(self.boardlength):
                            if int(temp_matrix0[j]) != 100:
                                temp_matrix[i][t] = temp_matrix0[j]
                                temp = temp_matrix0[j]
                                temp_matrix0[j] = 100

                                for k in range(self.boardlength):
                                    if int(temp_matrix1[k]) == temp:
                                        temp_matrix1[k] = 100
                                        break
                                break
                    else:
                        for j in range(self.boardlength):
                            if int(temp_matrix1[j]) != 100:
                                temp_matrix[i][t] = temp_matrix1[j]
                                temp = temp_matrix1[j]
                                temp_matrix1[j] = 100

                                for k in range(self.boardlength):
                                    if int(temp_matrix0[k]) == int(temp):
                                        temp_matrix0[k] = 100
                                        break
                                break

                for i in range(self.boardlength):
                    self.chromosome_matrix[i][2*index+self.population//2+t] = temp_matrix[i][t]

    def generate_crossovermatrix(self):
        for index in range(self.population):
            for a in range(self.boardlength):
                self.crossovermatrix[a][index] = random.randrange(32768) % 2

    def apply_mutation(self):
        number_mutation = int(self.mutation*(self.population-1)*self.boardlength)
        global rand_chromesome
        for k in range(number_mutation+1):
            rand_chromesome = 0
            while True:
                rand_chromesome = int(random.randrange(32768) % self.population)
                if rand_chromesome != 0:
                    break
            rand_gen0 = random.randrange(32768) % self.boardlength
            while True:
                rand_gen1 = random.randrange(32768) % self.boardlength
                if rand_gen1 != rand_gen0:
                    break

            temp = self.chromosome_matrix[rand_gen0][rand_chromesome]
            self.chromosome_matrix[rand_gen0][rand_chromesome] = self.chromosome_matrix[rand_gen1][rand_chromesome]
            self.chromosome_matrix[rand_gen0][rand_chromesome] = temp

    def fill_area(self, index):
        self.clear()
        for i in range(self.boardlength):
            self.area[i][int(self.chromosome_matrix[i][index])] = 1


def main():
    global mutation

    if len(sys.argv) < 4:
        print("Usage: {} <population> <iteration> <mutation_rate>".format(sys.argv[0]))
        population = 100
        iteration = 100
        mutation = 0.5
    else:
        population = sys.argv[1]
        iteration = sys.argv[2]
        mutation = sys.argv[3]

    sample = GAQueen(population=population, iteration=iteration, mutation=mutation)

    sample.initial_population()

    g = 0
    num = 0

    while g == 0 and num < sample.iteration:
        num += 1
        g = 0
        for k in range(sample.population):
            sample.fill_area(k)
            cost = sample.cost_func(k)
            sample.cost_matrix[k] = cost

            draw_plot(cost)

        sample.population_sort()

        if int(sample.cost_matrix[0]) == 0:
           g = 1

        sample.generate_crossovermatrix()
        sample.mating()
        sample.apply_mutation()

    res = '_'.join(str(int(sample.chromosome_matrix[i][0])) for i in range(N))
    print("result: {}".format(res))

    with open("final.csv", "w") as result:
        result.write("Final result: \n\t{}\n".format(res))
        result.write("\nAll solution:\n")
        result.close()
    plt.show()

    sample.find_solution()
    with open("final.csv", "a") as result:
        result.write("\n\tTotal: {} solution.\n".format(sample.solutions))
        result.close()
    print("finished.")


if __name__ == '__main__':
    main()

