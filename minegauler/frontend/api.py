"""
api.py - The API with the backend

December 2018, Lewis Gaul
"""

__all__ = ("AbstractController", "Listener")

import logging
import traceback
from typing import Dict

from minegauler.core.api import AbstractController, AbstractListener
from minegauler.core.grid import CoordType
from minegauler.types import CellContentsType, GameState

from .minefield import MinefieldWidget
from .panel import PanelWidget

logger = logging.getLogger(__name__)


class Listener(AbstractListener):
    """
    Concrete implementation of a listener to receive callbacks from the
    backend.
    """

    def __init__(self, gui, panel_widget: PanelWidget, mf_widget: MinefieldWidget):
        self._gui = gui
        self._panel_widget = panel_widget
        self._mf_widget = mf_widget

    def reset(self) -> None:
        """
        Called to indicate the state should be reset.
        """
        self._mf_widget.reset()
        self._panel_widget.reset()

    def update_cells(self, cell_updates: Dict[CoordType, CellContentsType]) -> None:
        for c, state in cell_updates.items():
            self._mf_widget.set_cell_image(c, state)

    def update_game_state(self, game_state: GameState) -> None:
        self._panel_widget.update_game_state(game_state)

    def update_mines_remaining(self, mines_remaining: int) -> None:
        self._panel_widget.set_mines_counter(mines_remaining)

    def set_finish_time(self, finish_time: float) -> None:
        """
        Called when a game has ended to pass the exact elapsed game time.

        :param finish_time:
            The elapsed game time in seconds.
        """
        self._panel_widget.timer.stop()
        self._panel_widget.timer.set_time(int(finish_time + 1))

    def handle_exception(self, method: str, exc: Exception) -> None:
        logger.error(
            "Error occurred when calling %s() from backend:\n%s\n%s",
            method,
            "".join(traceback.format_exception(None, exc, exc.__traceback__)),
            exc,
        )
