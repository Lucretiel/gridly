'''
monement.py - Facilities for moving entities around

This file contains the utilities for moving entities arond on a grid. The
movement system is designed to be very flexible and customizable. The primary
purpose of the movement system is to handle multiple entities moving around
in discrete steps, where all movement in a given step happens simultaniously.
Most of the work is in resolving collisions between entities and other objects
on the board.

The basic movement algorith is as follows:

Determine the desired locations of each entity.

Determine the CollisionType of each entity. It may be any one of the
following:
    non_moving: This entity isn't trying to move
    none: This entity isn't colliding with anything
    wall: This entity is colliding with the edge of the grid
    solid: This entity is colliding with a non-entity
    entity: This entity is colliding with an entity
    miss: This entity is moving on to a previously occupied space
    pending: This entity may collide with an entity

Determine resolution order- movement handler functions are called in a
deterministic order, once for each entity or group of entities. It is
important that as much automated resolution as possible happens before
these handling functions are called. A dependency graph is created, in
which each entity that is attempting to move onto a space with another
entity depends on it. Handling functions are then called in reverse order-
entities that depend on other entities have their handlers called after.
In some cases, multiple entities trying to move on to the same space can
create a circular dependency; in this case, a handler function decides
which entity gets to move out of the group, resolving the circle. In cases
where there are multiple choices for which handler to call next, location
sort order is used.

Call handlers- handlers are called in resolution order. The single entity
handlers can optionally return a CollisionResolution, which determines what
happens to the entity:
    proceed: For non-movng CollisionTypes, don't move the entity. Otherwise,
    move the entity.
    die: Kill the entity and remove it from the field.

The system is customized by providing rules:
    Accessor methods: These control access to the grid
    get_entity(grid, location): get an object from a grid
    pick_entity(grid, location): remove and return an object from the grid
    put_entity(grid, location, value): add an object to the grid
    move_entity(grid, location, destination): move an object. If not given,
    defaults to the equivelent of:
        put_entity(grid, destination, pick_entity(grid, location))
    is_empty(grid, location): return true if the location can be moved onto
    empty_object: default object for empty cells.


    Handlers: These are used to handle collision and movement. They are
    intended to implement light client logic, or resolve collisons.

    handle_movement(grid, entity)- called for all single entity movements,
    even non-collision movements. The entity object has a location,
    desired_location, and collision state. Its default behavior is to call
    handle_collision for collisions (wall, entity, and solid), and to call
    handle_type_{CollisionType} for the other collision types. The function
    can optionally return a CollisionResolution to indicate what should
    happen to the entity. Only certain CollisionResolutions apply to each
    CollisionType

    handle_collision(grid, entity)- called for all single entity collisions,
    which are wall, solid, and entity. Like with handle_movement, it can
    optionally return a CollisionResolution. Its default behavior is to call
    handle_type_{CollisionType}.

    handle_type_{CollisionType}(grid, entity) called for each individual
    CollisionType. Can return a CollisionResolution.

    default_resolutions- a dict that maps the various CollisionTypes to their
    default CollisionResolutions

    handle_group_collision(grid, destination, entities)- called when a group
    of entities are all trying to move on to the same space. May return
    the entity or location of the entity which should move. This function is
    called in addition to



'''

import enum
from gridly.location import Location, relative_locations
from gridly.direction import Direction


class CollisionType(enum.Enum):
    '''
    These are the different collision states an entity can be in
    '''
    non_moving = 0  # This entity isn't trying to move
    none = 1  # This entity isn't colliding with anything, but is moving
    wall = 2  # Collision with the edge of the grid
    solid = 3  # Collision with a non-entity
    entity = 4  # Collision with a non-moving entity
    miss = 5  # Avoided colliding with an entity
    pending = 6  # Potential collsion with an entity


class CollisionResolution(enum.Enum):
    '''
    These are the different resolutions an entity can have, for a given
    collision
    '''
    proceed = 1  # Don't kill the entity
    die = 2  # Kill the entity


class Entity:
    '''
    An entity is a moving object in the gridly movement system. It is used
    to wrap the various attributes (location, desired location, etc) of a
    moving object, as well as the underlying object on the grid
    '''
    def __init__(self, underlying, location, movement):
        self.underlying = underlying
        self.location = location
        self.desired_location = location + movement
        self.collision = CollisionType.unknown
        self.resolution = None


