import collections
import enum
from gridly.location import Location, relative_locations
from gridly.direction import Direction

class Entity(collections.namedtuple('Entity', ('underlying', 'location'))):
    pass


class CollisionType(enum.Enum):
    solid = 1 #Collision with a non-entity
    wall = 2 #Collision with the edge of the grid
    non_moving = 3 #Collision with a non-moving entity
    same_space = 4 #Two entities tried to move onto the same space
    pass_through = 5 #Two entities tried to pass through each other


class MovementHandler:
    def step(self, grid, object_movements):
        '''
        Run a step of the movement system. movements is a collections of
        pairs, where each pair is an object to move, and a movement,
        which is a Direction or Location.
        '''

    def convert_movement(self, grid, object_movement):
        entity, movement = object_movement
        if not isinstance(underlying, Entity):
            entity = Entity(grid[entity], Location(*entity))
        else:
            if grid[entity.location] is not entity.underlying:
                raise ValueError("Entity-Grid mismatch")

        if isinstance(movement, Direction):
            movement = relative_locations[movement]

        return entity, movement
