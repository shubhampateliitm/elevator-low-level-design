import sqlite3
from threading import Lock
from enums import Direction, DoorState # Assuming these are needed for state representation
import logging

class DatabaseManager:
    """Manages all database interactions for the elevator system, implemented as a Singleton."""
    _instance = None
    _lock = Lock()

    def __new__(cls, db_path: str = 'elevator_state.db'):
        """Ensures only one instance of DatabaseManager exists (Singleton pattern).

        Args:
            db_path (str): The path to the SQLite database file.

        Returns:
            DatabaseManager: The singleton instance of DatabaseManager.
        """
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance.db_path = db_path
                instance.conn = None
                instance.cursor = None
                instance._connect()
                instance._create_tables()
                cls._instance = instance
            return cls._instance

    def __init__(self, db_path: str = 'elevator_state.db') -> None:
        """Initializes the DatabaseManager. This method is a no-op for subsequent calls
        after the first instance creation due to the Singleton pattern.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        # __init__ is called every time __new__ is called, but we only want to initialize once.
        # The actual initialization is now handled in __new__ to ensure it happens only once.
        pass

    def _connect(self) -> None:
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False) # Allow multi-thread access for simplicity in simulation
            self.cursor = self.conn.cursor()
            logging.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")

    def _create_tables(self) -> None:
        """Creates the necessary tables in the database if they don't already exist."""
        try:
            # Elevator System State
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS elevator_system_state (
                    id INTEGER PRIMARY KEY,
                    num_floors INTEGER,
                    num_cars INTEGER
                )
            ''')
            # Elevator Car State
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS elevator_car_state (
                    car_id INTEGER PRIMARY KEY,
                    current_floor INTEGER,
                    direction TEXT,
                    current_state TEXT,
                    door_state TEXT,
                    door_open_time REAL
                )
            ''')
            # Elevator Car Requests (internal to car)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS elevator_car_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    car_id INTEGER,
                    floor INTEGER,
                    direction TEXT,
                    FOREIGN KEY (car_id) REFERENCES elevator_car_state(car_id)
                )
            ''')
            # System-wide Hall Call Requests
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    floor INTEGER,
                    direction TEXT
                )
            ''')
            self.conn.commit()
            logging.info("Database tables created/verified.")
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")

    def commit(self) -> None:
        """Commits the current transaction to the database."""
        if self.conn:
            try:
                self.conn.commit()
                logging.debug("Database transaction committed.")
            except sqlite3.Error as e:
                logging.error(f"Error committing transaction: {e}")

    def close(self) -> None:
        """Closes the database connection."""
        if self.conn:
            self.commit() # Commit any pending changes before closing
            self.conn.close()
            logging.info(f"Disconnected from database: {self.db_path}")

    def clear_all_data(self) -> None:
        """Clears all data from the elevator system tables. Useful for testing."""
        try:
            self.cursor.execute("DELETE FROM elevator_system_state")
            self.cursor.execute("DELETE FROM elevator_car_state")
            self.cursor.execute("DELETE FROM elevator_car_requests")
            self.cursor.execute("DELETE FROM system_requests")
            self.conn.commit()
            logging.info("All database data cleared.")
        except sqlite3.Error as e:
            logging.error(f"Error clearing database data: {e}")

    # --- Save Methods ---
    def save_system_state(self, num_floors: int, num_cars: int) -> None:
        """Saves the overall elevator system configuration state.

        Args:
            num_floors (int): Total number of floors.
            num_cars (int): Total number of elevator cars.
        """
        try:
            self.cursor.execute("INSERT OR REPLACE INTO elevator_system_state (id, num_floors, num_cars) VALUES (?, ?, ?)",
                                (1, num_floors, num_cars))
        except sqlite3.Error as e:
            logging.error(f"Error saving system state: {e}")

    def save_car_state(self, car_id: int, current_floor: int, direction: Direction, current_state: str, door_state: DoorState, door_open_time: float) -> None:
        """Saves the state of a specific elevator car.

        Args:
            car_id (int): The ID of the elevator car.
            current_floor (int): The current floor of the car.
            direction (Direction): The current direction of the car.
            current_state (str): The current operational state of the car (e.g., "IdleState").
            door_state (DoorState): The current state of the car's door.
            door_open_time (float): The timestamp when the door was opened.
        """
        try:
            self.cursor.execute("INSERT OR REPLACE INTO elevator_car_state (car_id, current_floor, direction, current_state, door_state, door_open_time) VALUES (?, ?, ?, ?, ?, ?)",
                                (car_id, current_floor, direction.name, current_state, door_state.name, door_open_time))
        except sqlite3.Error as e:
            logging.error(f"Error saving car state for car {car_id}: {e}")

    def save_car_requests(self, car_id: int, requests: list[tuple[int, Direction]]) -> None:
        """Saves the internal requests (car calls) for a specific elevator car.

        Args:
            car_id (int): The ID of the elevator car.
            requests (list[tuple[int, Direction]]): A list of (floor, direction) tuples representing car calls.
        """
        try:
            self.cursor.execute("DELETE FROM elevator_car_requests WHERE car_id = ?", (car_id,))
            for req_floor, req_direction in requests:
                self.cursor.execute("INSERT INTO elevator_car_requests (car_id, floor, direction) VALUES (?, ?, ?)",
                                    (car_id, req_floor, req_direction.name))
        except sqlite3.Error as e:
            logging.error(f"Error saving car requests for car {car_id}: {e}")

    def save_system_requests(self, requests: list[tuple[int, Direction]]) -> None:
        """Saves the system-wide hall call requests.

        Args:
            requests (list[tuple[int, Direction]]): A list of (floor, direction) tuples representing hall calls.
        """
        try:
            self.cursor.execute("DELETE FROM system_requests")
            for req_floor, req_direction in requests:
                self.cursor.execute("INSERT INTO system_requests (floor, direction) VALUES (?, ?)",
                                    (req_floor, req_direction.name))
        except sqlite3.Error as e:
            logging.error(f"Error saving system requests: {e}")

    # --- Load Methods ---
    def load_system_state(self) -> dict | None:
        """Loads the overall elevator system configuration state.

        Returns:
            dict | None: A dictionary containing 'num_floors' and 'num_cars', or None if not found.
        """
        try:
            self.cursor.execute("SELECT num_floors, num_cars FROM elevator_system_state WHERE id = 1")
            row = self.cursor.fetchone()
            if row:
                return {"num_floors": row[0], "num_cars": row[1]}
            return None
        except sqlite3.Error as e:
            logging.error(f"Error loading system state: {e}")
            return None

    def load_car_state(self, car_id: int) -> dict | None:
        """Loads the state of a specific elevator car.

        Args:
            car_id (int): The ID of the elevator car.

        Returns:
            dict | None: A dictionary containing the car's state, or None if not found.
        """
        try:
            self.cursor.execute("SELECT car_id, current_floor, direction, current_state, door_state, door_open_time FROM elevator_car_state WHERE car_id = ?", (car_id,))
            row = self.cursor.fetchone()
            if row:
                return {
                    "car_id": row[0],
                    "current_floor": row[1],
                    "direction": Direction[row[2]],
                    "current_state": row[3],
                    "door_state": DoorState[row[4]],
                    "door_open_time": row[5]
                }
            return None
        except sqlite3.Error as e:
            logging.error(f"Error loading car state for car {car_id}: {e}")
            return None

    def load_car_requests(self, car_id: int) -> list[tuple[int, Direction]]:
        """Loads the internal requests (car calls) for a specific elevator car.

        Args:
            car_id (int): The ID of the elevator car.

        Returns:
            list[tuple[int, Direction]]: A list of (floor, direction) tuples representing car calls.
        """
        try:
            self.cursor.execute("SELECT floor, direction FROM elevator_car_requests WHERE car_id = ?", (car_id,))
            rows = self.cursor.fetchall()
            requests = []
            for row in rows:
                requests.append((row[0], Direction[row[1]]))
            return requests
        except sqlite3.Error as e:
            logging.error(f"Error loading car requests for car {car_id}: {e}")
            return []

    def load_system_requests(self) -> list[tuple[int, Direction]]:
        """Loads the system-wide hall call requests.

        Returns:
            list[tuple[int, Direction]]: A list of (floor, direction) tuples representing hall calls.
        """
        try:
            self.cursor.execute("SELECT floor, direction FROM system_requests")
            rows = self.cursor.fetchall()
            requests = []
            for row in rows:
                requests.append((row[0], Direction[row[1]]))
            return requests
        except sqlite3.Error as e:
            logging.error(f"Error loading system requests: {e}")
            return []
