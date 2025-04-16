from pycsp3 import *
import numpy as np

path = 'layouts/Peaceful.sudoku'
with open(path, "r") as file:
            text = file.read()
            words = text.split()
            numbers = []
            for w in words:
                if w == "_":
                    numbers.append(0)
                else:
                    numbers.append(int(w))

x = VarArray(size=[9, 9], dom=range(1, 10))
clues = np.reshape(numbers, (9, 9)).tolist()    
for i in range(9):
   for j in range(9):
      if clues[i][j] > 0:
            satisfy(x[i][j] == clues[i][j])
    
for row in x:
   satisfy(AllDifferent(row))
    

for j in range(9):
   satisfy(AllDifferent([x[i][j] for i in range(9)]))
    
for block_row in range(3):
   for block_col in range(3):
       satisfy(
            AllDifferent(
                        x[i][j] 
                        for i in range(block_row * 3, block_row * 3 + 3)
                        for j in range(block_col * 3, block_col * 3 + 3)
                    )
                )
    

if solve(verbose=2) is SAT:
   solution = values(x)

print(solution)