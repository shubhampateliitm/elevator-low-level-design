import time
from elevator_system import ElevatorSystem
from enums import Direction
from database_manager import DatabaseManager # Import DatabaseManager
from logger_config import setup_logging # Import setup_logging
from config import NUM_FLOORS, NUM_CARS # Import configuration values
from elevator_component_factory import ElevatorComponentFactory # Import the new factory

def run_simulation(system):
    # Simulate some calls
    system.call_elevator(7, Direction.UP)
    system.call_elevator(3, Direction.DOWN)
    system.call_elevator(9, Direction.UP)

    # Main simulation loop
    for i in range(20): # Simulate for 20 time steps
        print(f"\n--- Time Step {i+1} ---") # Keep this print for simulation step clarity
        system.dispatcher()
        for car in system.get_cars():
            car.move()
        system.monitoring()
        system.save_state() # Save state at the end of each time step
        time.sleep(1)

def main():
    setup_logging() # Setup logging at the start of main
    
    # Use configuration values
    num_floors = NUM_FLOORS
    num_cars = NUM_CARS

    # Initialize DatabaseManager
    db_manager = DatabaseManager()

    # Initialize ElevatorComponentFactory
    factory = ElevatorComponentFactory()

    system = ElevatorSystem.initialize(num_floors, num_cars, dispatching_strategy=None, database_manager=db_manager, factory=factory)

    run_simulation(system)

    # Commit and close the database connection when done
    db_manager.commit()
    db_manager.close()

if __name__ == "__main__":
    main()
