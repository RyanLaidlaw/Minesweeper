import random

WIDTH = 30
HEIGHT = 16

class Autosolver:
    """
    Class that solves the minesweeper board

    Attributes: 
        board (list): the 2D list of the game board
        moves (list): a list of tuples (x, y, {action}) to return to the minesweeper board for solving
        first_move (tuple): (x, y, {action}) of the first move to play so the mines can be placed and the game can start
    """
    def __init__(self):
        self.board = []
        self.moves = []
        self.first_move = ()

    def set_board(self, board):
        self.board = board
    
    def get_board(self):
        return self.board
    
    def clear_moves(self):
        self.moves = []
    
    def retrieve_box(self, x, y):
        box = self.board[x][y] 
        return box

    def send_first_move(self):
        rand_x = random.randint(0, WIDTH - 1)
        rand_y = random.randint(0, HEIGHT - 1)
        self.first_move = (rand_x, rand_y, "uncover")
        return self.first_move
    
    def choose_continuation_points(self):
        random_continuation_points = []
        cur_box = self.retrieve_box(self.first_move[0], self.first_move[1])
        while cur_box.get_mine_neighbor_count() != 0:
            rand_x = random.randint(0, WIDTH - 1)
            rand_y = random.randint(0, HEIGHT - 1)
            move = (rand_x, rand_y, "uncover")
            random_continuation_points.append(move)
            cur_box = self.retrieve_box(rand_x, rand_y)
        return random_continuation_points

    def solve(self, board):
        self.set_board(board)
        continuation_points = self.choose_continuation_points()
        self.moves.extend(continuation_points)
        return self.moves