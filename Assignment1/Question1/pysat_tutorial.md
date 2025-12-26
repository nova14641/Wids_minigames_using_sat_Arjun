# PySAT Tutorial

This tutorial introduces the basics of using the PySAT toolkit to solve SAT problems.

## Installation

Install PySAT using pip:

```bash
pip install python-sat[pblib,aiger]
```

## Basic Usage

```python
from pysat.formula import CNF
from pysat.solvers import Solver

# Create a CNF formula
cnf = CNF()

# Example: (x1 ∨ ¬x2) ∧ (¬x1 ∨ x3)
cnf.append([1, -2])
cnf.append([-1, 3])

# Initialize a SAT solver
with Solver(name='glucose3') as solver:
    solver.append_formula(cnf.clauses)
    if solver.solve():
        model = solver.get_model()
        print("SAT solution:", model)
    else:
        print("UNSAT")
```

## Notes

- PySAT does not parse DIMACS files directly in code mode; use the `CNF` object instead.
- Always call `solver.solve()` before accessing `solver.get_model()`.
- Use `-x` to represent ¬x in a clause.
