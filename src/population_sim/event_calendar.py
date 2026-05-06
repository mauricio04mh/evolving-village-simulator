import heapq
import itertools
import logging
from typing import Optional

from population_sim.event import Event


class EventCalendar:
    def __init__(self, end_time: float, logger: Optional[logging.Logger] = None):
        self.end_time = end_time
        self._events = []
        self._sequence_counter = itertools.count()
        self._logger = logger

    def schedule(self, time: float, priority: int, event_type: str, data: dict):
        if time > self.end_time:
            self._log_discarded_event(time, priority, event_type, data)
            return

        sequence = next(self._sequence_counter)

        event = Event(
            time=time,
            priority=priority,
            sequence=sequence,
            event_type=event_type,
            data=data,
        )

        heapq.heappush(self._events, event)
        self._log_event("enqueue", event)

    def has_events(self) -> bool:
        return len(self._events) > 0

    def pop_next(self) -> Event:
        event = heapq.heappop(self._events)
        self._log_event("dequeue", event)
        return event

    def _log_event(self, action: str, event: Event):
        if self._logger is None:
            return

        self._logger.info(
            "queue=%s time=%.6f priority=%d sequence=%d type=%s data=%s queue_size=%d",
            action,
            event.time,
            event.priority,
            event.sequence,
            event.event_type,
            event.data,
            len(self._events),
        )

    def _log_discarded_event(
        self,
        time: float,
        priority: int,
        event_type: str,
        data: dict,
    ):
        if self._logger is None:
            return

        self._logger.info(
            "queue=discarded time=%.6f priority=%d type=%s data=%s queue_size=%d reason=time_gt_end_time",
            time,
            priority,
            event_type,
            data,
            len(self._events),
        )
