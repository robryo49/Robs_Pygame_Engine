"""Process-pool manager for submitting and resolving asynchronous tasks."""

from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Optional, Callable

from .async_process import AsyncProcess


class AsyncProcessManager:
    """Submits work to a process pool and resolves completed tasks.

    Submitted callables and arguments must be picklable, so avoid passing live
    pygame objects or bound methods that close over them.
    """

    def __init__(self, max_workers: Optional[int] = None) -> None:
        """Create a process pool manager.

        :param max_workers: Maximum number of worker processes, using the executor default when omitted.
        """
        self._executor = ProcessPoolExecutor(max_workers=max_workers)
        self._handles: list[AsyncProcess] = []

    @property
    def pending_count(self) -> int:
        """Return the number of handles still awaiting resolution."""
        return len(self._handles)

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> AsyncProcess:
        """Submit a callable and return its process handle.

        :param fn: Callable to run in the process pool.
        :param args: Positional arguments forwarded to the callable.
        :param kwargs: Keyword arguments forwarded to the callable.
        :return: A handle tracking the submitted future.
        """
        future = self._executor.submit(fn, *args, **kwargs)
        handle = AsyncProcess(future)
        self._handles.append(handle)
        return handle

    def update(self) -> AsyncProcessManager:
        """Resolve all futures that have completed.

        :return: This manager for chained calls.
        """
        still_pending: list[AsyncProcess] = []

        for handle in self._handles:
            if handle.future.done():
                handle.resolve()
                if handle.exception is not None:
                    logging.error("AsyncProcessManager task failed: %r", handle.exception)
            else:
                still_pending.append(handle)

        self._handles = still_pending
        return self

    def shutdown(self, wait: bool = True) -> None:
        """Shut down the underlying process pool.

        :param wait: Whether to wait for pending work to finish before returning.
        """
        self._executor.shutdown(wait=wait)
