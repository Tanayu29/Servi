from abc import ABC, abstractmethod

class BaseAgent(ABC):
    name = "BaseAgent"

    @abstractmethod
    def execute(self, request: dict) -> dict:
        pass
