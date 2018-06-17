"""
game_logic.py - The core game logic

April 2018, Lewis Gaul

Exports:
  Controller
    Controller class, implementing game logic and providing callback functions.
    Arguments:
      x_size - Number of columns
      y_size - Number of rows
      game_mode (optional) - Mode specifying which game logic to use
    Attributes:
      board - The current board state
"""

from PyQt5.QtCore import pyqtSlot

from minegauler.callback_core import core as cb_core
from minegauler.utils import Grid, GameCellMode, CellState, GameState
from .utils import Board
from .minefield import Minefield


#@@@
mines = 7
per_cell = 2
first_success = True


class Controller:
    """
    Class for processing all game logic. Implements callback functions for
    'clicks'.
    """
    def __init__(self, x_size, y_size, game_mode=GameCellMode.NORMAL):
        self.x_size = x_size
        self.y_size = y_size
        self.game_mode = game_mode
        self.mines_remaining = mines
        # Initialise game board.
        self.board = Board(x_size, y_size)
        # Callbacks from the UI.
        cb_core.leftclick.connect(self.leftclick)
        cb_core.rightclick.connect(self.rightclick)
        cb_core.bothclick.connect(self.bothclick)
        cb_core.new_game.connect(self.new_game)
        cb_core.end_game.connect(self.end_game)
        # Keeps track of whether the minefield has been created yet.
        self.game_state = GameState.READY
    
    # @pyqtSlot(tuple)
    def leftclick(self, coord):
        """
        Callback for a left-click on a cell.
        """
        if (self.game_state not in [GameState.READY, GameState.ACTIVE]
            or self.board[coord] != CellState.UNCLICKED):
            return
            
        # Check if first click.
        if self.game_state == GameState.READY:
            # Create the minefield.
            if first_success:
                safe_coords = self.mf.get_nbrs(*coord, include_origin=True)
            else:
                safe_coords = []
            self.mf.create(mines, per_cell, safe_coords)
            self.game_state = GameState.ACTIVE
            cb_core.start_game.emit()

        # Mine hit.
        if self.mf.cell_contains_mine(*coord):
            self.set_cell(coord, CellState.HITS[self.mf[coord]])
            for c in self.mf.all_coords:
                if self.mf.cell_contains_mine(*c) and c != coord:
                    self.set_cell(c, CellState.MINES[self.mf[c]])
            cb_core.end_game.emit(GameState.LOST)
        # Opening hit.
        elif self.mf.completed_board[coord] == CellState.NUM0:
            for opening in self.mf.openings:
                if coord in opening:
                    # Found the opening, quit the loop here.
                    break
            for c in opening:
                if self.board[c] == CellState.UNCLICKED:
                    self.set_cell(c, self.mf.completed_board[c])
        # Reveal clicked cell only.
        else:
            self.set_cell(coord, self.mf.completed_board[coord])
        
        self.check_for_completion()
    
    # @pyqtSlot(tuple)
    def rightclick(self, coord):
        """
        Callback for a right-click on a cell.
        """
        if self.game_state not in [GameState.READY, GameState.ACTIVE]:
            return
        if self.game_mode == GameCellMode.NORMAL:
            if self.board[coord] == CellState.UNCLICKED:
                self.set_cell(coord, CellState.FLAG1)
                self.mines_remaining -= 1
            elif self.board[coord] in CellState.FLAGS:
                if self.board[coord] == CellState.FLAGS[per_cell]:
                    self.set_cell(coord, CellState.UNCLICKED)
                    self.mines_remaining += per_cell
                else:
                    self.set_cell(coord, self.board[coord] + 1)
                    self.mines_remaining -= 1
            cb_core.set_mines_counter.emit(self.mines_remaining)
        
        elif self.game_mode == GameCellMode.SPLIT:
            if self.board[coord] == CellState.UNCLICKED:
                self.split_cell(coord)
    
    # @pyqtSlot(tuple)
    def bothclick(self, coord):
        """
        Callback for a left-and-right-click on a cell.
        """
        if (self.game_state not in [GameState.READY, GameState.ACTIVE]
            or self.board[coord] != CellState.UNCLICKED):
            return
            
    def set_cell(self, coord, state):
        """
        Set a cell to be in the given state, calling registered callbacks.
        """
        self.board[coord] = state
        cb_core.set_cell.emit(coord, state)
                        
    def check_for_completion(self):
        """
        Check if game is complete by comparing self.board to
        self.mf.completed_board, and if it is call relevent 'end game' methods.
        """
        # Assume (for contradiction) that game is complete.
        is_complete = True
        for c in self.mf.all_coords:
            exp_val = self.mf.completed_board[c]
            if exp_val in CellState.NUMS and exp_val != self.board[c]:
                is_complete = False
                break
        if is_complete:
            for c in self.mf.all_coords:
                if self.mf.cell_contains_mine(*c):
                    self.set_cell(c, CellState.FLAGS[self.mf[c]])
            cb_core.end_game.emit(GameState.WON)
    
    # @pyqtSlot()
    def new_game(self):
        """Create a new game."""
        self.game_state = GameState.READY
        self.mines_remaining = mines
        cb_core.set_mines_counter.emit(mines)
        self.mf = Minefield(self.x_size, self.y_size)
        for c in self.board.all_coords:
            self.set_cell(c, CellState.UNCLICKED)
            
    # @pyqtSlot(GameState)
    def end_game(self, game_state):
        """
        End a game.
        Arguments:
          game_state (GameState)
            GameState.WON or GameState.LOST.
        """
        self.game_state = game_state
        if game_state == GameState.WON:
            cb_core.set_mines_counter.emit(0)


if __name__ == '__main__':
    # from .stubs import StubUI, StubMinefieldUI
    ctrlr = Controller(3, 5)
    # ui = StubUI(procr)
    # mf_ui = StubMinefieldUI(procr)

