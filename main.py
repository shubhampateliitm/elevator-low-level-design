import time
from elevator_system import ElevatorSystem
from enums import Direction

def run_simulation(system):
    # Simulate some calls
    system.call_elevator(7, Direction.UP)
    system.call_elevator(3, Direction.DOWN)
    system.call_elevator(9, Direction.UP)

    # Main simulation loop
    for i in range(20): # Simulate for 20 time steps
        print(f"\n--- Time Step {i+1} ---")
        system.dispatcher()
        for car in system.get_cars():
            car.move()
        system.monitoring()
        time.sleep(1)

def main():
    num_floors = 13
    num_cars = 3

    system = ElevatorSystem.get_instance(num_floors, num_cars, dispatching_strategy=None)

    run_simulation(system)

if __name__ == "__main__":
    main()
