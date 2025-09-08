# clock.py
from typing import Iterator, Optional

class Clock:
    def __init__(
        self,
        delta_time_usec: int,
        start_usec: int = 0,
        global_end_usec: Optional[int] = None
    ):
        self.delta = int(max(1, delta_time_usec))
        self.now = int(max(0, start_usec))
        self.global_end = int(global_end_usec) if global_end_usec is not None else None

    def seek(self, usec: int):
        self.now = int(max(0, usec))
