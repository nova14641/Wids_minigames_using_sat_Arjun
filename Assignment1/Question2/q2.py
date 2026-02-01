from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

class SokobanEncoder:
    def __init__(self, grid, T):
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.player_start = None
        self.walls = set()

        self._parse_grid()
        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        for r in range(self.N):
            for c in range(self.M):
                char = self.grid[r][c]
                if char == 'P':
                    self.player_start = (r, c)
                elif char == 'B':
                    self.boxes.append((r, c))
                elif char == 'G':
                    self.goals.append((r, c))
                elif char == '#':
                    self.walls.add((r, c))
                elif char == '*': # Box on Goal
                    self.boxes.append((r, c))
                    self.goals.append((r, c))
                elif char == '+': # Player on Goal
                    self.player_start = (r, c)
                    self.goals.append((r, c))

    def var_player(self, r, c, t):
        # Unique ID for player at (r, c) at time t
        # Range: 1 to (N*M*(T+1))
        return (t * self.N * self.M) + (r * self.M + c) + 1

    def var_box(self, b_idx, r, c, t):
        # Unique ID for box b_idx at (r, c) at time t
        # Offset by the max player variables
        offset = (self.T + 1) * self.N * self.M
        box_vars_per_step = self.num_boxes * self.N * self.M
        return offset + (t * box_vars_per_step) + (b_idx * self.N * self.M) + (r * self.M + c) + 1

    def encode(self):
        N, M, T = self.N, self.M, self.T

        # 1. Initial conditions
        # Player start position
        pr, pc = self.player_start
        self.cnf.append([self.var_player(pr, pc, 0)])
        for r in range(N):
            for c in range(M):
                if (r, c) != (pr, pc):
                    self.cnf.append([-self.var_player(r, c, 0)])

        # Boxes start positions
        for i, (br, bc) in enumerate(self.boxes):
            self.cnf.append([self.var_box(i, br, bc, 0)])
            for r in range(N):
                for c in range(M):
                    if (r, c) != (br, bc):
                        self.cnf.append([-self.var_box(i, r, c, 0)])

        # 2. Constraints for each timestep
        for t in range(T):
            # A: Player must be exactly in one position
            self.cnf.append([self.var_player(r, c, t) for r in range(N) for c in range(M)])
            for r1 in range(N):
                for c1 in range(M):
                    v1 = self.var_player(r1, c1, t)
                    for r2 in range(N):
                        for c2 in range(M):
                            if (r1, c1) < (r2, c2):
                                self.cnf.append([-v1, -self.var_player(r2, c2, t)])

            # B: Box must be exactly in one position
            for i in range(self.num_boxes):
                self.cnf.append([self.var_box(i, r, c, t) for r in range(N) for c in range(M)])

            # C: Walls and Collisions
            for r in range(N):
                for c in range(M):
                    if (r, c) in self.walls:
                        self.cnf.append([-self.var_player(r, c, t)])
                        for i in range(self.num_boxes):
                            self.cnf.append([-self.var_box(i, r, c, t)])
                    
                    # Two boxes cannot occupy the same cell
                    for i in range(self.num_boxes):
                        for j in range(i + 1, self.num_boxes):
                            self.cnf.append([-self.var_box(i, r, c, t), -self.var_box(j, r, c, t)])

            # D: Movement Transitions (The "Action" Logic)
            for r in range(N):
                for c in range(M):
                    if (r, c) in self.walls: continue
                    
                    p_curr = self.var_player(r, c, t)
                    
                    possible_next_positions = []
                    for move, (dr, dc) in DIRS.items():
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < N and 0 <= nc < M and (nr, nc) not in self.walls:
                            possible_next_positions.append(self.var_player(nr, nc, t+1))
                            
                            # E: Box Pushing Logic
                            nnr, nnc = nr + dr, nc + dc
                            for i in range(self.num_boxes):
                                b_at_target = self.var_box(i, nr, nc, t)
                                if 0 <= nnr < N and 0 <= nnc < M and (nnr, nnc) not in self.walls:
                                    b_pushed = self.var_box(i, nnr, nnc, t + 1)
                                    # (P_t & B_t & P_t+1) -> B_t+1
                                    self.cnf.append([-p_curr, -b_at_target, -self.var_player(nr, nc, t+1), b_pushed])
                                else:
                                    self.cnf.append([-p_curr, -b_at_target, -self.var_player(nr, nc, t+1)])

                    # F: Box Inertia (If no push, box stays)
                    for i in range(self.num_boxes):
                        b_curr = self.var_box(i, r, c, t)
                        b_next = self.var_box(i, r, c, t + 1)
                        self.cnf.append([-b_curr, b_next, self.var_player(r, c, t + 1)])

        # 3. Goal conditions (Final timestep T)
        for i in range(self.num_boxes):
            goal_clauses = []
            for (gr, gc) in self.goals:
                goal_clauses.append(self.var_box(i, gr, gc, T))
            self.cnf.append(goal_clauses)
            
        return self.cnf


def decode(model, encoder):
    moves = []
    for t in range(encoder.T):
        p_pos_t = None
        p_pos_next = None
        for r in range(encoder.N):
            for c in range(encoder.M):
                if model[encoder.var_player(r, c, t) - 1] > 0:
                    p_pos_t = (r, c)
                if model[encoder.var_player(r, c, t + 1) - 1] > 0:
                    p_pos_next = (r, c)
        
        if p_pos_t and p_pos_next:
            dr, dc = p_pos_next[0] - p_pos_t[0], p_pos_next[1] - p_pos_t[1]
            for move, (mdr, mdc) in DIRS.items():
                if (dr, dc) == (mdr, mdc):
                    moves.append(move)
                    break
    return moves
