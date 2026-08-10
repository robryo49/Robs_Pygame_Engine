from concurrent.futures import Future
from typing import Any, Optional

from robs_pge.utils.management_tools.types import Callback


class AsyncProcess:
    def __init__(self, future: Future):
        self._future = future

        self._done = False
        self._result: Any = None
        self._used: bool = False

        self._exception: Optional[BaseException] = None

        self._on_complete: Callback[[Any], None] = None

    # region PROPERTIES

    @property
    def future(self):
        return self._future

    @property
    def done(self) -> bool:
        return self._done

    @property
    def used(self):
        return self._used

    @property
    def result(self) -> Any:
        if not self._done:
            raise RuntimeError("GenerationHandle has no result yet; check `.done` before accessing `.result`")
        if self._exception is not None:
            raise self._exception
        return self._result

    @property
    def exception(self) -> Optional[BaseException]:
        return self._exception

    # endregion

    def on_complete(self, callback: Callback[[Any], None]) -> "AsyncProcess":
        self._on_complete = callback
        return self

    def resolve(self) -> None:
        try:
            self._result = self._future.result()
        except BaseException as e:
            self._exception = e
        finally:
            self._done = True

        if self._exception is None and self._on_complete is not None:
            if isinstance(self._on_complete, tuple):
                for cb in self._on_complete:
                    cb(self._result)
            else:
                self._on_complete(self._result)

    def use_result(self):
        self._used = True
        return self.result

