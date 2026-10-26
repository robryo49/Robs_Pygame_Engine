"""Handle for a future submitted to the asynchronous process manager."""

from __future__ import annotations

from concurrent.futures import Future
from typing import Any, Optional

from ..management_tools import Callback


class AsyncProcess:
    """Wraps a submitted future and resolves it when complete."""

    def __init__(self, future: Future[Any]) -> None:
        """Create a process handle around a submitted future.

        :param future: Future whose result or exception will be captured.
        """
        self._future = future

        self._done = False
        self._result: Any = None
        self._used = False
        self._exception: Optional[BaseException] = None
        self._on_complete: Callback[[Any], None] = None

    @property
    def future(self) -> Future[Any]:
        """Return the wrapped future."""
        return self._future

    @property
    def done(self) -> bool:
        """Return whether the process has been resolved."""
        return self._done

    @property
    def used(self) -> bool:
        """Return whether the result has been consumed through ``use_result``."""
        return self._used

    @property
    def result(self) -> Any:
        """Return the resolved result, raising any captured exception.

        :return: The result produced by the future.
        :raises RuntimeError: If the process has not been resolved yet.
        :raises BaseException: The exception captured by the future, re-raised unchanged.
        """
        if not self._done:
            raise RuntimeError("AsyncProcess has no result yet; check `.done` before accessing `.result`")
        if self._exception is not None:
            raise self._exception
        return self._result

    @property
    def exception(self) -> Optional[BaseException]:
        """Return the exception captured during resolution, if any."""
        return self._exception

    def on_complete(self, callback: Callback[[Any], None]) -> AsyncProcess:
        """Set the callback invoked when this process resolves successfully.

        :param callback: Callback or tuple of callbacks receiving the result.
        :return: This process handle for chained calls.
        """
        self._on_complete = callback
        return self

    def resolve(self) -> None:
        """Resolve the future and invoke the completion callbacks once."""
        try:
            self._result = self._future.result()
        except BaseException as exc:
            self._exception = exc
        finally:
            self._done = True

        if self._exception is None and self._on_complete is not None:
            if isinstance(self._on_complete, tuple):
                for callback in self._on_complete:
                    callback(self._result)
            else:
                self._on_complete(self._result)

    def use_result(self) -> Any:
        """Return the result and mark it as consumed.

        :return: The resolved result.
        """
        self._used = True
        return self.result

    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"AsyncProcess(done={self.done}, used={self.used})"
