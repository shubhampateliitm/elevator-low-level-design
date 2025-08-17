from elevator_state import IdleState, MovingUpState, MovingDownState, MaintenanceState

class ElevatorStateFactory:
    """
    A factory for creating ElevatorState objects based on their string names.
    This centralizes the logic for re-instantiating state objects from persistence.
    """
    _state_map = {
        "IdleState": IdleState,
        "MovingUpState": MovingUpState,
        "MovingDownState": MovingDownState,
        "MaintenanceState": MaintenanceState
    }

    @classmethod
    def create_state(cls, state_name: str, car: object) -> object:
        """
        Creates an ElevatorState object given its string name and the ElevatorCar instance.

        Args:
            state_name (str): The string name of the state (e.g., "IdleState").
            car (object): The ElevatorCar instance to which the state belongs.

        Returns:
            object: An instance of the specified ElevatorState.

        Raises:
            ValueError: If an unknown state name is provided.
        """
        state_class = cls._state_map.get(state_name)
        if state_class:
            return state_class(car)
        else:
            raise ValueError(f"Unknown elevator state: {state_name}")
