import heapq
import itertools

from population_sim.event import Event


class EventCalendar:
    def __init__(self, end_time: float):
        self.end_time = end_time
        self._events = []
        self._sequence_counter = itertools.count()

    def schedule(self, time: float, priority: int, event_type: str, data: dict):
        if time > self.end_time:
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

    def has_events(self) -> bool:
        return len(self._events) > 0

    def pop_next(self) -> Event:
        return heapq.heappop(self._events)