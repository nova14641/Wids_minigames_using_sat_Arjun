import hashlib
import math
import os
import csv
from q1 import solve_sudoku
from typing import List
from tqdm import tqdm
import random

def is_valid_sudoku(original: List[List[int]], grid: List[List[int]]) -> bool:
    n = len(original)
    sqrtn = int(n**0.5)

    for i in range(n):
        for j in range(n):
            if original[i][j] != 0 and original[i][j] != grid[i][j]:
                return False


    for i in range(n):
        if set(grid[i]) != set(range(1, n+1)):  
            return False
        col = [grid[r][i] for r in range(n)]
        if set(col) != set(range(1, n+1)): 
            return False


    for box_row in range(0, n, sqrtn):
        for box_col in range(0, n, sqrtn):
            block = []
            for i in range(sqrtn):
                for j in range(sqrtn):
                    block.append(grid[box_row+i][box_col+j])
            if set(block) != set(range(1, n+1)):
                return False

    return True

puzzles = []

with open('testcases', 'r') as f:
    lines = f.readlines()

# Filter valid lines of length 81
valid_lines = [line.strip() for line in lines if len(line.strip()) == 81]

# Randomly sample 500 lines without replacement
sampled_lines = random.sample(valid_lines, min(500, len(valid_lines)))

# Convert each line to a 9x9 grid
for line in sampled_lines:
    grid = [
        [int(c) if c.isdigit() else 0 for c in line[i*9:(i+1)*9]]
        for i in range(9)
    ]
    puzzles.append(grid)



passed = 0

for i, puzzle in enumerate(tqdm(puzzles, desc="Solving puzzles")):
    solved = solve_sudoku(puzzle)
    if is_valid_sudoku(puzzle, solved):
        passed += 1
    else:
        print(f"❌ Test case {i + 1} failed!")

print(f"\n✅ {passed}/{len(puzzles)} test cases passed.")

