import enum
from gridly.location import Location


class Direction(Location, enum.Enum):
    '''Enum to reperesent each of the 4 directions'''
    up = Location.zero().above()
    down = Location.zero().below()
    left = Location.zero().left()
    right = Location.zero().right()
