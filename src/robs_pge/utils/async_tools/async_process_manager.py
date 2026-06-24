import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Optional

from .async_process import AsyncProcess


class AsyncProcessManager:
    def __init__(self, max_workers: Optional[int] = None):
        self._executor: ProcessPoolExecutor = ProcessPoolExecutor(max_workers=max_workers)
        self._handles: list[AsyncProcess] = []
    
    # region PROPERTIES
    
    @property
    def pending_count(self) -> int:
        return len(self._handles)
    
    # endregion
    
    def submit(self, fn: Callable, *args, **kwargs) -> AsyncProcess:
        future = self._executor.submit(fn, *args, **kwargs)
        handle = AsyncProcess(future)
        self._handles.append(handle)
        return handle
    
    def update(self) -> "AsyncProcessManager":
        still_pending = []
        
        for handle in self._handles:
            if handle.future.done():
                handle.resolve()
                if handle.exception is not None:
                    logging.error(f"AsyncGeneratorManager task failed: {handle.exception!r}")
            else:
                still_pending.append(handle)
        
        self._handles = still_pending
        
        return self
    
    def shutdown(self, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait)

