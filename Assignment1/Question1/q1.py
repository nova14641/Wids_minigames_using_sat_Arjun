from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    n = 9
    cnf = CNF()
    def v(r, c, val):
        return r * 81 + c * 9 + val
    for r in range(n):
        for c in range(n):
            cnf.append([v(r, c, val) for val in range(1, n + 1)])
    for r in range(n):
        for c in range(n):
            for v1 in range(1, n + 1):
                for v2 in range(v1 + 1, n + 1):
                    cnf.append([-v(r, c, v1), -v(r, c, v2)])
    for r in range(n):
        for val in range(1, n + 1):
            cnf.append([v(r, c, val) for c in range(n)])
    for c in range(n):
        for val in range(1, n + 1):
            cnf.append([v(r, c, val) for r in range(n)])
    for br in range(0, n, 3):
        for bc in range(0, n, 3):
            for val in range(1, n + 1):
                cnf.append([v(br + r, bc + c, val) for r in range(3) for c in range(3)])
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                cnf.append([v(r, c, grid[r][c])])
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model = solver.get_model()
            res = [[0 for _ in range(n)] for _ in range(n)]
            for lit in model:
                if lit > 0:
                    val = (lit - 1) % 9 + 1
                    c = ((lit - 1) // 9) % 9
                    r = (lit - 1) // 81
                    res[r][c] = val
            return res
        else:
            return None
