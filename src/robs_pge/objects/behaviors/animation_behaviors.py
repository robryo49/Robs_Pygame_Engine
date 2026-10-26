"""Behaviors that react to events, input, collisions, and attribute changes on pygame objects."""

from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from .behavior import ObjectBehavior
from .action_behaviors import ActionOnAttributeChangeBehavior
from ..object_flags import ObjectFlags
from ...animation import Animation, AnimationManager
from ...utils import vec2

if TYPE_CHECKING:
    pass


class AnimationOnClickBehavior(ObjectBehavior):
    """Play animations when the owner is clicked and released with a given mouse button."""
    def __init__(self, button: int, click_animation: Optional[Callable[[], Animation]] = None, release_animation: Optional[Callable[[], Animation]] = None) -> None:
        """
        Store the button and animation factories.

        :param button: Mouse button that triggers the animations.
        :param click_animation: Factory returning the animation to play on press.
        :param release_animation: Factory returning the animation to play on release.
        """
        super().__init__()

        self._button = button
        self._click_animation = click_animation
        self._release_animation = release_animation

        self._animation_manager: Optional[AnimationManager] = None

    def on_attach(self) -> None:
        """Cache the animation manager and mark the owner as clickable."""
        if (owner := self.owner) is None: return
        self._animation_manager = owner.services.get_animation_manager()
        owner.add_flag(ObjectFlags.CLICKABLE)

    def on_click(self, button: int, pos: vec2) -> None:
        """
        Play the click animation when the configured button is pressed.

        :param button: Mouse button that was pressed.
        :param pos: Pointer position in world coordinates.
        """
        if not self._animation_manager or not self._click_animation: return
        if button == self._button:
            self._animation_manager.play(self._click_animation())

    def on_release(self, button: int, pos: vec2) -> None:
        """
        Play the release animation when the configured button is released.

        :param button: Mouse button that was released.
        :param pos: Pointer position in world coordinates.
        """
        if not self._animation_manager or not self._release_animation: return
        if button == self._button:
            self._animation_manager.play(self._release_animation())

class AnimationOnHoverBehavior(ObjectBehavior):
    """Play animations when the pointer enters and leaves the owner."""
    def __init__(self, hover_start_animation: Optional[Callable[[], Animation]] = None, hover_end_animation: Optional[Callable[[], Animation]] = None) -> None:
        """
        Store the hover animation factories.

        :param hover_start_animation: Factory returning the animation to play when hovering begins.
        :param hover_end_animation: Factory returning the animation to play when hovering ends.
        """
        super().__init__()

        self._hover_start_animation = hover_start_animation
        self._hover_end_animation = hover_end_animation

        self._animation_manager: Optional[AnimationManager] = None

    def on_attach(self) -> None:
        """Cache the animation manager and mark the owner as clickable."""
        if (owner := self.owner) is None: return
        self._animation_manager = owner.services.get_animation_manager()
        owner.add_flag(ObjectFlags.CLICKABLE)

    def on_hover_start(self) -> None:
        """Play the animation configured for the start of hovering."""
        if not self._animation_manager or not self._hover_start_animation: return
        self._animation_manager.play(self._hover_start_animation())

    def on_hover_end(self) -> None:
        """Play the animation configured for the end of hovering."""
        if not self._animation_manager or not self._hover_end_animation: return
        self._animation_manager.play(self._hover_end_animation())

class AnimationOnAttributeChangeBehavior(ActionOnAttributeChangeBehavior):
    """Play an animation when a watched owner attribute changes."""
    def __init__(self, attribute: str, animation: Optional[Callable[[], Animation]]) -> None:
        """
        Store the watched attribute and animation factory.

        :param attribute: Name of the owner attribute to watch.
        :param animation: Factory returning the animation to play when the attribute changes.
        """
        super().__init__(attribute, lambda o: o.play_animation(animation()))

