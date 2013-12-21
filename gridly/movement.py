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
    pending: This entity MAY collide with an entity (There is an entity
        on this entity's desired location whose final movement is
        indeterminant.)

Resolve group collisions- for every set of more than one entity trying
to move on to a given location, decide which on gets to move with the
resolce_group_collison rule. Note that there is no guarentee that it will
actually move. Each entity involved in a group collision may choose to
either stay, die, or move, though only up to one may move.

Resolve movement chains. During this step, any entities with the pending
movement state are checked. If there is a cycle of pending movement,
all involved entites may move.

Handle individual movements. This is where client logic for movement
and collision is handled. At this point, the client may choose to kill
entities.

The system is customized by providing rules:
    get_entity(grid, location): get an object from a grid
    pick_entity(grid, location): remove an object from the grid
    put_entity(grid, location, value): add an object to the grid
    is_empty(grid, location): return true if the location cannot be moved onto
    empty_object: default object for empty cells.

    resolve_group_collision(grid, entities, target_location, target_entity=None):
        Core function for collision handling. Called for every group of
        entities trying to move onto a given location in an arbitrary order.
        The arguments to this function are the grid, a list of entities,
        the location they are trying to move on to, and if it exists,
        the entity currently occupying this location.
        In addition to performing any client logic, this function should
        return the location of the entity that gets to move, or None. It
        may also set the resolution of each Up to one
        of them may get a move resolution. The entity with a move resolution
        will only move if there is no target_entity, or if it doesn't
        move. After being called, the resolution is cleared, and each
        enitty not chosen to move is given a non_moving CollisionType.
        If more than one entity is chosen to move, the move is aborted
        and a RuntimeError is raised. Its default behavior is to prevent
        any movement (All entities get the stay resolution)

    handle_movement(grid, entity, target_entity=None)
        This is called once for each entity. It is called after group
        collisions and movement chains are resolved. Its arguments are the
        entity being processed and, if it exists, the entity on the location
        being moved to. This function is called for all entitites, including
        those with non_moving and none collision types. Its default behavior
        is to call handle_type_none, hanlde_type_non_moving, or
        handle_collision.

    handle_collision(grid, entity, target_entity=None)
        This is called by resolve_movement for the CollisionTypes that are
        actually collisions. It otherwise has the same semantics as
        resolve_movement. Its default behavior is to call
        resolve_type_{CollisionType}.

    handle_type_{CollisionType}
        Called by resolve_movement or resolve_collision to resolve the
        individual collision. Can contain client

Logic Ordering and Determinsim:
It is important that movement resolution be deterministic. In an ideal
world, the client logic is designed such that the end result is the same
no matter what order it is called in. However, there's no way to guarentee
that, so rules are in place that describe the order that the resolve_*
and handle_* rules are called.

The basic rule of thumb is that at each stage, the methods are called in
sorted order of the desired location. However, in the event of an acyclic
dependency chain, handlers at the dependency-free end of the chain are
called before the handlers that depend on them. For instance:

    |>>>|

Say you have the 3 entities above, all moving right. Under the sorted order
rules, they would be called left-to-right. However, under the dependency
rules, they will be called right-to-left. The reason is that the rightmost
entity might choose to stay or die. Depending on its choice, the middle
entity will have its CollisionType updated from pending to either none
or entity.

The same rules apply to group collisions. For instance:

    | VV |
    |>>  |
    |  ^<|
    |  ^ |

In this example, there are 3 group collisions. The top right one will
be resolved first, because of dependency



Note also that there is no guarentee that, in an acyclic movement dependency
chain, the various entities in the change will be handled exactly one after
the other. The only guarentee is that entitites earlier in the dependency
chain will be handled earlier than those later in the chain.
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

    # Internal Use
    pending = -1  # This entity is colliding with an object whos movement is unknown
    unknown = -2  # Calculations haven't been made for this entity


class CollisionResolution(enum.Enum):
    '''
    These are the different resolutions an entity can have, for a given
    collision
    '''
    stay = 1  # Do not move the entity
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


