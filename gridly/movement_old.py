from collections import defaultdict
import enum
from gridly.location import Location, relative_locations
from gridly.direction import Direction

class CollisionType(enum.Enum):
    none = 0  # This entity isn't colliding with anything, but is moving
    non_moving = 1  # This entity isn't trying to move
    wall = 2  # Collision with the edge of the grid
    solid = 3  # Collision with a non-entity
    with_non_moving = 4  # Collision with a non-moving entity
    with_same_desired = 5  # Collision with an entity trying to end on the same space

    # Internal Use
    pending = -1  # This entity is colliding with an object under determination
    unknown = -2  # Calculations haven't been made for this entity

non_moving = {
    CollisionType.solid,
    CollisionType.wall,
    CollisionType.non_moving
}

class CollisionResolution(enum.Enum):
    unset = 0
    stay = 1
    move = 2
    die = 3


class Entity:
    def __init__(self, underlying, location, movement):
        self.underlying = underlying
        self.location = location
        self.desired_location = location + movement
        self.collision = CollisionType.unknown
        self.resolution = CollisionResolution.unset

'''
Basic algorithm for movement:
Determine each entity's desired position. Create a dependency chain- if
entity A desires to move onto a location where entity B resides, A depends
on B. If B can move, A can move; otherwise, A collides with B. If there
is a cycle, all entities can move.
'''

'''
Rules list:
    get_entity(grid, location)  # Get an enitity
    pick_entity(grid, location)  # "pick up" (remove from board) an enitity
    put_entity(grid, location, entity)  # "place" (put on board) an entity
    is_empty(grid, location)  # True if a location is empty
    empty_object = None # default behavior for is_empty and pick_entity

    # RESOLVERS
    # Resolve an entity's collision. Must assign a CollisionResolution to
    # the entity
    handle_collision(grid, entity)

    # Resolve an entity's collision of a given type. Must assign a
    # CollisionResolution to the entity. One function for each type of
    # collision, excluding the internal use types. The default
    # handle_collision method calls these, and falls back to the resolutions
    # dict. Generally, these should only be provided for the CollisionTypes
    # that are actually collisions, as the system will automatically handle
    # unencumbered movement. As a counterexample, you could add a
    # handle_collision_non_moving resolver that returns die, to prevent
    # entities from not trying to move.
    handle_collision_{CollisionType}(grid, entity)
    ...

    # If given, resolve the collisions of a list of entities, all with the
    # same desired location. Otherwise, defer back to
    # handle_collision_with_same_desired
    handle_all_same_desired(grid, entity_list)

    # If given, resolve the a collision between a moving and nonmoving
    # entity
    handle_nonmoving_collision(grid, moving, nonmoving)

    # Note that all resolvers MUST set the resolution of the entities they
    # resolve, otherwise a ValueError must be raised.
'''

class MovementHandler:
    ####################################################################
    # RULES
    ####################################################################

    # Grid manipulation and access
    def get_entity(self, grid, location):
        return grid[location]

    def pick_entity(self, grid, location):
        grid[location] = self.empty_object

    def put_entity(self, grid, location, entity):
        grid[location] = entity

    def is_empty(self, grid, location):
        return grid[location] == self.empty_object

    # Default behaviors
    resolutions = {
        CollisionType.none: CollisionResolution.move,
        CollisionType.non_moving: CollisionResolution.stay,
        CollisionType.wall: CollisionResolution.stay,
        CollisionType.solid: CollisionResolution.stay,
        CollisionType.with_non_moving: CollisionResolution.stay,
        CollisionType.with_same_desired: CollisionResolution.stay,
    }

    def handle_collision(self, grid, entity):
        collision_func = 'handle_collision_{}'.format(entity.collision.name)
        resolution = None
        if hasattr(self, collision_func):
            resolution = getattr(self, collision_func)(grid, entity)
        if resolution is None:
            resolution = resolutions[entity.collision]
        return resolution

    ####################################################################
    # Movement
    ####################################################################
    def make_entity(self, grid, location, movement):
        '''
        Create an entity based on a grid location and a desired movement
        '''
        location, movement = object_movements
        if isinstance(movement, Direction):
            movement = relative_locations[movement]
        return Entity(get_entity(grid, location), location, movement)

    def resolve_movements(self, grid, object_movements):
        '''
        Given a grid, and a series of object movements, perform all
        movements, while calling all collision functions. object_movements
        is a collection of (location, movement) pairs, where each movement
        is a direction or a relative location
        '''

        #Dict of all entities, keyed by location
        entities = {location: self.make_entity(grid, location, movement)
            for location, movement in object_movements}

        #Dict of how many entities desire a given location
        desired_location_entities = defaultdict(int)
        for location, entity in entities.items():
            desired_location_entities[entity.location] += 1

        #Function to find the collision of an individual entity
        def solve(self, grid, entity):
            '''
            Solve the collision of a single entity
            '''
            #Only resolve entities with unknown status
            if entity.collision is not CollisionType.unknown
                return

            desired_location = entity.desired_location
            location = entity.location
            #Is it moving at all?
            if location == desired_location:
                entity.collision = self_non_moving
                return

            #Is it trying to move off the grid?
            if not grid.valid(location):
                entity.collision = CollisionType.wall
                return

            #Is there already an entity there?
            try:
                target_entity = entities[desired_location]
                if target_entity.resolution is CollisionResolution.stay:
                    entity.collision = CollisionType.with_non_moving
                    return
                elif target_entity.resolution is CollisionResolution.unset:
                    entity.collision = CollisionType.pending
                    return
            except KeyError:
                pass

            #Is another entity trying to go to the same spot?
            if desired_location_entities[entity] > 1:
                entity.collision = CollisionType.with_same_desired
                return

            #Can we move there at all?
            if self.is_empty(grid, location):
                entity.collision = CollisionType.none
            else:
                entity.collision = CollisionType.solid

        for location, entity in entities.items():





