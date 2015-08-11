#!/usr/bin/env python3
from config import *
from enum import Enum
from queue import Queue

NEIGHBOURS = [(x, y) for x in range(-1, 2) \
                     for y in range(-1, 2) if not (y == 0 and x == 0)]
CELLS = [(x, y) for x in range(1, BOARD_SIZE+1) for y in range(1, BOARD_SIZE+1)]

class SellState(Enum):
    empty, firstPoint, secondPoint = 0, 1, 2
    firstAliveComm, secondAliveComm = 3, 4
    firstDeadComm, secondDeadComm = 5, 6

FIRST_ALIVES = (SellState.firstPoint, SellState.firstAliveComm)
SECOND_ALIVES = (SellState.secondPoint, SellState.secondAliveComm)

class Game:
    def __init__(self):
        self.field = [[SellState.empty for y in range(BOARD_SIZE+2)] \
                                       for x in range(BOARD_SIZE+2)]
        self.turn = 0
        self.moves_left = 2
        self.captures = 0

    def make_move(self, x, y):
        if (x, y) not in self.get_allowed_moves():
            return False
        if self.turn == 0:
            if self.field[x][y] == SellState.empty:
                self.field[x][y] = SellState.firstPoint
            elif self.field[x][y] == SellState.secondPoint:
                self.field[x][y] = SellState.firstAliveComm
                self.captures += 1
        elif self.turn == 1:
            if self.field[x][y] == SellState.empty:
                self.field[x][y] = SellState.secondPoint
            elif self.field[x][y] == SellState.firstPoint:
                self.field[x][y] = SellState.secondAliveComm
                self.captures += 1
        self.update_field()
        self.moves_left -= 1

        if self.moves_left == 0:
            self.turn = 1 if self.turn == 0 else 0
            self.moves_left = 3
            self.captures = 0
        return True

    def update_field(self):
        for x, y in CELLS:
            if self.field[x][y] == SellState.firstAliveComm:
                self.field[x][y] = SellState.firstDeadComm
            if self.field[x][y] == SellState.secondAliveComm:
                self.field[x][y] = SellState.secondDeadComm

        for x, y in CELLS:
            # First player
            if self.field[x][y] in FIRST_ALIVES:
                q = Queue()
                q.put((x, y))
                while not q.empty():
                    cur_x, cur_y = q.get()
                    for sh_x, sh_y in NEIGHBOURS:
                        n_x, n_y = cur_x + sh_x, cur_y + sh_y
                        if self.field[n_x][n_y] == SellState.firstDeadComm:
                            self.field[n_x][n_y] = SellState.firstAliveComm
                            q.put((n_x, n_y))

            # Second player
            if self.field[x][y] in SECOND_ALIVES:
                q = Queue()
                q.put((x, y))
                while not q.empty():
                    cur_x, cur_y = q.get()
                    for sh_x, sh_y in NEIGHBOURS:
                        n_x, n_y = cur_x + sh_x, cur_y + sh_y
                        if self.field[n_x][n_y] == SellState.secondDeadComm:
                            self.field[n_x][n_y] = SellState.secondAliveComm
                            q.put((n_x, n_y))

    def get_field(self):
        tfield = []
        for i in range(1, BOARD_SIZE+1):
            tfield.append([i.value for i in self.field[i][1:BOARD_SIZE+1]])
        return tfield

    def get_allowed_moves(self):
        allow_capture = bool(self.captures < 2)
        allowed_moves = set()

        if self.turn == 0 and self.field[1][1] == SellState.empty:
            allowed_moves.add((1, 1))
            return list(allowed_moves)
        elif self.turn == 1 and self.field[BOARD_SIZE][BOARD_SIZE] == SellState.empty:
            allowed_moves.add((BOARD_SIZE, BOARD_SIZE))
            return list(allowed_moves)

        for x, y in CELLS:
            if self.field[x][y] in FIRST_ALIVES and self.turn == 0:
                for sh_x, sh_y in NEIGHBOURS:
                    n_x, n_y = x + sh_x, y + sh_y
                    if not (1 <= n_x <= BOARD_SIZE and 1 <= n_y <= BOARD_SIZE):
                        continue
                    if self.field[n_x][n_y] == SellState.empty or (allow_capture \
                                 and self.field[n_x][n_y] == SellState.secondPoint):
                        allowed_moves.add((n_x, n_y))
            elif self.field[x][y] in SECOND_ALIVES and self.turn == 1:
                for sh_x, sh_y in NEIGHBOURS:
                    n_x, n_y = x + sh_x, y + sh_y
                    if not (1 <= n_x <= BOARD_SIZE and 1 <= n_y <= BOARD_SIZE):
                        continue
                    if self.field[n_x][n_y] == SellState.empty or (allow_capture \
                                 and self.field[n_x][n_y] == SellState.firstPoint):
                        allowed_moves.add((n_x, n_y))
        return list(allowed_moves)

    def get_points(self):
        self.update_field()
        for x, y in CELLS:
            if self.field[x][y] in FIRST_ALIVES:
                if self.field[x][y] == SellState.firstPoint:
                    self.field[x][y] = SellState.firstAliveComm
                q = Queue()
                q.put((x, y))
                while not q.empty():
                    cur_x, cur_y = q.get()
                    for sh_x, sh_y in NEIGHBOURS:
                        n_x, n_y = cur_x + sh_x, cur_y + sh_y
                        if self.field[n_x][n_y] == SellState.empty:
                            self.field[n_x][n_y] = SellState.firstAliveComm
                            q.put((n_x, n_y))
            if self.field[x][y] in SECOND_ALIVES:
                if self.field[x][y] == SellState.secondPoint:
                    self.field[x][y] = SellState.secondAliveComm
                q = Queue()
                q.put((x, y))
                while not q.empty():
                    cur_x, cur_y = q.get()
                    for sh_x, sh_y in NEIGHBOURS:
                        n_x, n_y = cur_x + sh_x, cur_y + sh_y
                        if self.field[n_x][n_y] == SellState.empty:
                            self.field[n_x][n_y] = SellState.secondAliveComm
                            q.put((n_x, n_y))

        points = [0, 0]
        for x, y in CELLS:
            if self.field[x][y] == SellState.firstAliveComm:
                points[0] += 1
            elif self.field[x][y] == SellState.secondAliveComm:
                points[1] += 1
        return points, self.get_field()

    def __str__(self):
        return ("\n".join([" ".join(str(i.value) \
                           for i in self.field[x][1:BOARD_SIZE+1]) \
                           for x in range(1, BOARD_SIZE+1)]) \
                + "\n" + str(self.turn))

    def from_str(self, s):
        for x, line in enumerate(s.splitlines()):
            if x == BOARD_SIZE:
                self.turn = int(line)
                continue
            for y, value in enumerate(line.split(" ")):
                self.field[x+1][y+1] = SellState(int(value))
