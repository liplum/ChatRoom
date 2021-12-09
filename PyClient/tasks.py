from collections import deque
from typing import Deque, Callable

Total = int
Count = int
StepMode = Callable[[Total], Count]


def byPercent(percent: float) -> StepMode:
    def func(total: Total) -> Count:
        return round(percent * total + 0.5)

    return func


def byCount(max_count: int) -> StepMode:
    def func(total: Total) -> Count:
        return max_count if total > max_count else total

    return func


DefaultStepMode = byCount(1)


class task_runner:
    def __init__(self, step_mode: StepMode = DefaultStepMode):
        self.tasks: Deque = deque()
        self._step = step_mode

    @property
    def step_mode(self) -> StepMode:
        return self._step

    @step_mode.setter
    def step_mode(self, value: StepMode):
        self._step = value

    def add(self, task: Callable):
        self.tasks.append(task)

    def run_all(self):
        tasks = self.tasks
        while len(tasks) > 0:
            task = tasks.popleft()
            task()

    def run_step(self):
        tasks = self.tasks
        count = self.step_mode(len(tasks))
        while count > 0 and len(tasks) > 0:
            task = self.tasks.popleft()
            task()
            count -= 1
