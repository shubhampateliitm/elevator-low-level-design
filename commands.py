from enum import Enum

class Command(Enum):
    SET_DIRECTION = "set_direction"
    SET_STATE = "set_state"
    INCREMENT_FLOOR = "increment_floor"
    DECREMENT_FLOOR = "decrement_floor"
    ADD_UP_REQUEST = "add_up_request"
    ADD_DOWN_REQUEST = "add_down_request"
    REMOVE_UP_REQUEST = "remove_up_request"
    REMOVE_DOWN_REQUEST = "remove_down_request"
    OPEN_DOOR_AND_NOTIFY = "open_door_and_notify"
