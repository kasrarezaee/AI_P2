import numpy as np 
from pycsp3 import *
from myCSP.mycsp import *
from board import Board
from refresher import *

class Layout:
    """
    Represents a Sudoku puzzle layout and provides methods to solve it using different CSP algorithms.

    This class reads a Sudoku layout from a file, initializes the puzzle grid, and provides solving functions
    using both PyCSP and a our csp solver, mycsp (YAY!!!). The solutions enforce constraints such as row, 
    column, and 3x3 block uniqueness, and allow for various heuristic optimizations.

    Attributes:
        clues (list[list[int]]): A 9x9 grid representing the initial Sudoku puzzle state.
    """
    def __init__(self, path):
        """Initializes the Sudoku layout by reading a file and parsing the puzzle grid."""
        with open(path, "r") as file:
            text = file.read()
            words = text.split()
            numbers = []
            for w in words:
                if w == "_":
                    numbers.append(0)
                else:
                    numbers.append(int(w))

        self.clues = np.reshape(numbers, (9, 9)).tolist()

    def get_clues(self):
        """Returns the initial Sudoku clues."""
        return self.clues

        
    def pycsp_solve(self, board: Board) -> bool:
        """
    Solves the Sudoku puzzle using the PyCSP3 solver.
    Returns True if solution found, False otherwise.
    """
        
        clear()
        clues = board.layout_board
        x = VarArray(size=[9, 9], dom=range(1, 10))
        for i in range(9):
            for j in range(9):
                if clues[i][j] > 0:
                    satisfy(x[i][j] ==clues[i][j])
    

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
    
        if solve() is SAT:
            solution = values(x)
            print(solution)
            for i in range(9):
                for j in range(9):
                    board.answer_board[i][j] = solution[i][j]
                
            return True
    
        return False
    
    def mycsp_solve(self, 
                board: Board,
                do_unary_check: bool, 
                do_arc_consistency: bool, 
                do_mrv: bool,
                do_lcv: bool,
                real_time: bool,
                refresh: Callable[[],None],
                get_stop_event: Callable[[], bool]) -> bool:
        """
    Solves the Sudoku puzzle using our custom mycsp solver.
    Returns True if a solution is found, False otherwise.
    """
        from myCSP.mycsp import my_satisfy, my_solve, my_clear, myVarArray, myUnaryConstraint, myAllDifferent

    
    # Clear previous CSP state
        my_clear()

    # Initialize variables (9x9 grid with domain 1-9)
        x = myVarArray("test" , size=[9, 9], dom=range(1, 10))
        clues = board.layout_board
        
    # Apply unary constraints (fixed initial values)
        for i in range(9):
            for j in range(9):
                if clues[i][j] > 0:
                    my_satisfy(myUnaryConstraint(
                        x[i][j], 
                        relation="=",
                        num=clues[i][j]
                    ))
                    
    # Apply AllDifferent constraints for rows
        for row in x:
            my_satisfy(myAllDifferent(row))

    # Apply AllDifferent constraints for columns
        for j in range(9):
            column = [x[i][j] for i in range(9)]
            my_satisfy(myAllDifferent(column))

    # Apply AllDifferent constraints for 3x3 blocks
        for block_row in range(3):
            for block_col in range(3):
                block = [
                    x[i][j]
                    for i in range(block_row * 3, block_row * 3 + 3)
                    for j in range(block_col * 3, block_col * 3 + 3)
                ]
                my_satisfy(myAllDifferent(block))

    # Initialize Refresher for GUI updates
        #refresher = Refresher(board, refresh, get_stop_event)
        refresher = Refresher(
            vars=x,                # The myVarArray of variables
            board=board,           # The Board object
            real_time=real_time,   # Whether to update in real-time
            refresh=refresh,       # GUI update callback
            get_stop_event=get_stop_event  # Stop-check callback
        )

    # Solve using mycsp
        if my_solve(
            do_unary_check=do_unary_check,
            do_arc_consistency=do_arc_consistency,
            do_mrv=do_mrv,
            do_lcv=do_lcv,
            refresher=refresher
        ):
        # Copy solution to board.answer_board
            for i in range(9):
                for j in range(9):
                    board.answer_board[i][j] = x[i][j].value

            return True
        return False

    def mycsp_solve1(self, 
                    board: Board,
                    do_unary_check: bool, 
                    do_arc_consistency: bool, 
                    do_mrv: bool,
                    do_lcv: bool,
                    real_time: bool,
                    refresh: Callable[[],None],
                    get_stop_event: Callable[[], bool]) -> bool:
        """
        Solves the Sudoku puzzle using our csp solver (mycsp) with various heuristics.
        Returns True if solution found, False otherwise.
        """
        # YOUR CODE
    
    def solve(self, 
              algorithm: str, 
              do_unary_check: bool, 
              do_arc_consistency: bool, 
              do_mrv: bool,
              do_lcv: bool,
              real_time: bool, 
              board: Board,
              refresh: Callable[[],bool],
              get_stop_event: Callable[[], bool]):
        """Solves the Sudoku puzzle using the selected CSP algorithm."""
        if algorithm == 'p':
            return self.pycsp_solve(board)
        else:
            return self.mycsp_solve(board, do_unary_check, 
                                    do_arc_consistency, 
                                    do_mrv, 
                                    do_lcv, 
                                    real_time, 
                                    refresh,
                                    get_stop_event)