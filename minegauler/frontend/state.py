"""
state.py - State shared by any of the frontend modules

December 2019, Lewis Gaul
"""

__all__ = ("HighscoreWindowState", "PerGameState", "State")

import logging
from typing import Dict, Optional

import attr

from .. import shared, types, utils


logger = logging.getLogger(__name__)


@attr.attrs(auto_attribs=True)
class PerGameState(utils.StructConstructorMixin):
    """State that applies to an in-progress game."""

    x_size: int = 8
    y_size: int = 8
    mines: int = 10
    first_success: bool = True
    per_cell: int = 1
    lives: int = 1
    drag_select: bool = False


class HighscoreWindowState(utils.StructConstructorMixin):
    """State associated with the highscores window."""

    name_filter: Optional[str] = None
    name_hint: str = ""
    flagging_filter: Optional[str] = None
    sort_by: str = "time"
    current_highscore: Optional[shared.HighscoreStruct] = None


@attr.attrs(auto_attribs=True, kw_only=True)
class State:
    """All state shared between widgets."""

    _current_game_state: PerGameState = PerGameState()
    _pending_game_state: Optional[PerGameState] = None

    btn_size: int = 16
    name: str = ""
    styles: Dict[types.CellImageType, str] = {
        types.CellImageType.BUTTONS: "Standard",
        types.CellImageType.NUMBERS: "Standard",
        types.CellImageType.MARKERS: "Standard",
    }

    _game_status: types.GameState = types.GameState.READY

    ui_mode: types.UIMode = types.UIMode.GAME

    highscores_state: HighscoreWindowState = HighscoreWindowState()

    # ---------------------------------
    # Handling for game state fields
    # ---------------------------------
    def _update_game_state(self, field: str, value) -> None:
        if self.game_status is types.GameState.READY:
            setattr(self._current_game_state, field, value)
        else:
            setattr(self.pending_game_state, field, value)

    @property
    def x_size(self):
        return self._current_game_state.x_size

    @x_size.setter
    def x_size(self, value):
        self._update_game_state("x_size", value)

    @property
    def pending_x_size(self):
        if self.has_pending_game_state():
            return self.pending_game_state.x_size
        else:
            return self._current_game_state.x_size

    @property
    def y_size(self):
        return self._current_game_state.y_size

    @y_size.setter
    def y_size(self, value):
        self._update_game_state("y_size", value)

    @property
    def pending_y_size(self):
        if self.has_pending_game_state():
            return self.pending_game_state.y_size
        else:
            return self._current_game_state.y_size

    @property
    def mines(self):
        return self._current_game_state.mines

    @mines.setter
    def mines(self, value):
        self._update_game_state("mines", value)

    @property
    def difficulty(self) -> str:
        return shared.get_difficulty(self.x_size, self.y_size, self.mines)

    @property
    def pending_mines(self):
        if self.has_pending_game_state():
            return self.pending_game_state.mines
        else:
            return self._current_game_state.mines

    @property
    def first_success(self):
        return self._current_game_state.first_success

    @first_success.setter
    def first_success(self, value):
        self._update_game_state("first_success", value)

    @property
    def pending_first_success(self):
        if self.has_pending_game_state():
            return self.pending_game_state.first_success
        else:
            return self._current_game_state.first_success

    @property
    def per_cell(self):
        return self._current_game_state.per_cell

    @per_cell.setter
    def per_cell(self, value):
        self._update_game_state("per_cell", value)

    @property
    def pending_per_cell(self):
        if self.has_pending_game_state():
            return self.pending_game_state.per_cell
        else:
            return self._current_game_state.per_cell

    @property
    def lives(self):
        return self._current_game_state.lives

    @lives.setter
    def lives(self, value):
        self._update_game_state("lives", value)

    @property
    def pending_lives(self):
        if self.has_pending_game_state():
            return self.pending_game_state.lives
        else:
            return self._current_game_state.lives

    @property
    def drag_select(self):
        return self._current_game_state.drag_select

    @drag_select.setter
    def drag_select(self, value):
        self._update_game_state("drag_select", value)

    @property
    def pending_drag_select(self):
        if self.has_pending_game_state():
            return self.pending_game_state.drag_select
        else:
            return self._current_game_state.drag_select

    @property
    def pending_game_state(self) -> PerGameState:
        if self.has_pending_game_state():
            return self._pending_game_state
        else:
            return self._current_game_state

    @pending_game_state.setter
    def pending_game_state(self, value: Optional[PerGameState]):
        self._pending_game_state = value

    def has_pending_game_state(self) -> bool:
        return self._pending_game_state is not None

    def _activate_pending_game_state(self) -> None:
        if self._pending_game_state:
            self._current_game_state = self._pending_game_state
            self._pending_game_state = None

    @property
    def game_status(self) -> types.GameState:
        return self._game_status

    @game_status.setter
    def game_status(self, value: types.GameState):
        self._game_status = value
        if value is types.GameState.READY and self.has_pending_game_state():
            logger.info(
                "Updating game state on new game from %s to %s",
                self._current_game_state,
                self.pending_game_state,
            )
            self._activate_pending_game_state()

    # ---------------------------------
    # Methods for instance creation
    # ---------------------------------
    def deepcopy(self) -> "State":
        cls = type(self)
        pending_game_state = None
        if self.has_pending_game_state():
            pending_game_state = self.pending_game_state.copy()
        return cls(
            current_game_state=self._current_game_state.copy(),
            pending_game_state=pending_game_state,
            btn_size=self.btn_size,
            name=self.name,
            styles=self.styles.copy(),
        )

    @classmethod
    def from_opts(
        cls, game_opts: shared.GameOptsStruct, gui_opts: shared.GUIOptsStruct
    ) -> "State":
        dict_ = {**attr.asdict(game_opts), **attr.asdict(gui_opts)}
        args = {a: v for a, v in dict_.items() if a in attr.fields_dict(cls)}
        args["current_game_state"] = PerGameState.from_structs(game_opts, gui_opts)
        return cls(**args)
