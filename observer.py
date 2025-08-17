from abc import ABC, abstractmethod

class Subject(ABC):
    """The Subject interface declares a set of methods for managing subscribers."""

    @abstractmethod
    def attach(self, observer) -> None:
        """Attach an observer to the subject."""
        pass

    @abstractmethod
    def detach(self, observer) -> None:
        """Detach an observer from the subject."""
        pass

    @abstractmethod
    def notify(self, event: str, data: dict = None) -> None:
        """Notify all observers about an event.

        Args:
            event (str): The type of event that occurred.
            data (dict, optional): Additional data related to the event. Defaults to None.
        """
        pass


class Observer(ABC):
    """The Observer interface declares the update method, used by subjects."""

    @abstractmethod
    def update(self, subject: Subject, event: str, data: dict = None) -> None:
        """Receive update from subject."""
        pass
