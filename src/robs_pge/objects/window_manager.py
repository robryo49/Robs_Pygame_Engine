"""Registration and state management for scene windows."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ..events import Event, EventManager, Events

if TYPE_CHECKING:
    from ..objects import WindowObject


class WindowManager:
    """Registers windows and manages opening, closing, and exclusive groups."""

    def __init__(self, event_manager: EventManager) -> None:
        """
        Initialize a window manager that emits window events.

        :param event_manager: Event manager used to emit window lifecycle events.
        """
        self._event_manager = event_manager
        self._windows: dict[str, WindowObject] = {}
        self._groups: dict[str, set[str]] = {}
        self._window_group: dict[str, str] = {}

    @property
    def windows(self) -> dict[str, WindowObject]:
        """Return the registered windows keyed by ID."""
        return self._windows

    def register(self, window: WindowObject, group: Optional[str] = None) -> WindowObject:
        """
        Register a window, optionally within an exclusive group.

        :param window: Window to register.
        :param group: Optional exclusive group name.
        :return: The registered window.
        """
        window_id = window.id
        old_group = self._window_group.get(window_id)
        if old_group is not None:
            self._groups[old_group].discard(window_id)
            if not self._groups[old_group]:
                self._groups.pop(old_group)

        self._windows[window_id] = window
        window.hide()
        if group:
            self._groups.setdefault(group, set()).add(window_id)
            self._window_group[window_id] = group
        else:
            self._window_group.pop(window_id, None)
        return window

    def is_open(self, window_id: str | WindowObject) -> bool:
        """
        Return whether the supplied window is open.

        :param window_id: Window identifier or window instance.
        :return: ``True`` when the window is open.
        """
        window = self._get_window(window_id)
        return window.opened

    def open(self, window_id: str | WindowObject) -> WindowManager:
        """
        Open a window and close other open windows in its group.

        :param window_id: Window identifier or window instance.
        :return: This window manager.
        """
        resolved_id = self._resolve_id(window_id)
        window = self._get_window(resolved_id)

        group = self._window_group.get(resolved_id)
        if group is not None:
            for other_id in tuple(self._groups[group]):
                if other_id != resolved_id:
                    self.close(other_id)

        window.open()
        self._event_manager.trigger(Event(Events.WINDOW_OPENED, window_id=resolved_id))
        return self

    def close(self, window_id: str | WindowObject) -> WindowManager:
        """
        Close a window if it is open.

        :param window_id: Window identifier or window instance.
        :return: This window manager.
        """
        resolved_id = self._resolve_id(window_id)
        window = self._get_window(resolved_id)

        if window.opened:
            window.close()
            self._event_manager.trigger(Event(Events.WINDOW_CLOSED, window_id=resolved_id))
        return self

    def toggle(self, window_id: str | WindowObject) -> WindowManager:
        """
        Toggle a window's open state.

        :param window_id: Window identifier or window instance.
        :return: This window manager.
        """
        return self.close(window_id) if self.is_open(window_id) else self.open(window_id)

    def close_all(self) -> WindowManager:
        """
        Close every open window.

        :return: This window manager.
        """
        for window_id in tuple(self._windows):
            self.close(window_id)
        return self

    def unregister(self, window_id: str | WindowObject) -> WindowObject:
        """
        Close and remove a registered window.

        :param window_id: Window identifier or window instance.
        :return: The removed window.
        """
        resolved_id = self._resolve_id(window_id)
        window = self._get_window(resolved_id)

        if window.opened:
            self.close(resolved_id)

        group = self._window_group.pop(resolved_id, None)
        if group is not None:
            self._groups[group].discard(resolved_id)
            if not self._groups[group]:
                self._groups.pop(group)

        return self._windows.pop(resolved_id)

    def _resolve_id(self, window_id: str | WindowObject) -> str:
        """
        Return a window ID from a string or window instance.

        :param window_id: Window identifier or window instance.
        :return: The resolved window identifier.
        """
        return window_id if isinstance(window_id, str) else window_id.id

    def _get_window(self, window_id: str | WindowObject) -> WindowObject:
        """
        Resolve and return a registered window, raising when it is missing.

        :param window_id: Window identifier or window instance.
        :return: The registered window.
        :raises KeyError: When the window is not registered.
        """
        resolved_id = self._resolve_id(window_id)
        window = self._windows.get(resolved_id)
        if window is None:
            raise KeyError(f"Window with id '{resolved_id}' does not exist or isn't registered")
        return window
