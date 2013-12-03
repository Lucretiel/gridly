import collections
from gridly.direction import Direction

class Location(collections.namedtuple('Location', ('row', 'column'))):
    '''
    Location reperesents a location in a 2D row-column space. It is primarily
    a helper class over regular tuples of (row, column). It assumes that +row
    is down and +column is right.
    '''
    @classmethod
    def zero(cls):
        '''
        Create a (0, 0) initialized Location

        >>> Location.zero()
        Location(row=0, column=0)
        '''
        return cls(0, 0)

    def __add__(self, other):
        '''
        Adds 2 Locations, memberwise.

        >>> Location(1, 2) + Location(3, 4)
        Location(row=4, column=6)
        '''
        return Location(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other):
        '''
        Subtracts 2 Locations, memberwise.

        >>> Location(4, 4) - Location(1, 2)
        Location(row=3, column=2)
        '''
        return Location(self[0] - other[0], self[1] - other[1])

    def above(self, distance=1):
        '''
        Return the location above this one, at the specified distance

        >>> Location(2, 3).above()
        Location(row=1, column=3)
        '''
        return Location(self[0]-distance, self[1])

    def below(self, distance=1):
        '''
        Return the location below this one, at the specified distance

        >>> Location(2, 3).below()
        Location(row=3, column=3)
        '''
        return Location(self[0]+distance, self[1])

    def left(self, distance=1):
        '''
        Return the location to the left of this one, at the specified distance

        >>> Location(2, 3).left()
        Location(row=2, column=2)
        '''
        return Location(self[0], self[1]-distance)

    def right(self, distance=1):
        '''
        Return the location to the right of this one, at the specified distance

        >>> Location(2, 3).right()
        Location(row=2, column=4)
        '''
        return Location(self[0], self[1]+distance)

    #directions is a mapping of directions to the relative location functions above
    directions = {
        Direction.up: above,
        Direction.down: below,
        Direction.left: left,
        Direction.right: right
    }

    def relative(self, direction, distance=1):
        '''
        Returns the location in the direction specified, at the specified distance

        >>> Location.zero().relative(Direction.down)
        Location(row=1, column=0)
        '''
        return Location.directions[direction](self, distance)

    def path(self, *directions):
        '''
        Given 1 or more directions, follows all of them in sequence, and returns
        the final location.

        >>> Location.zero().path(Direction.down, Direction.right, Direction.down)
        Location(row=2, column=1)
        '''
        loc = self
        for d in directions:
            loc = loc.relative(d)
        return loc

    def each_at(self, *directions):
        '''
        Given a series of directions or paths (where a path is an ordered
        collection of directions), yield each relative directions.

        >>> list(Location(1, 1).each_at(Direction.up, Direction.left, (Direction.right, Direction.down)))
        [Location(row=0, column=1), Location(row=1, column=0), Location(row=2, column=2)]
        '''
        for direct in directions:
            if isinstance(direct, Direction):
                yield self.relative(direct)
            else:
                yield self.path(*direct)

    def adjacent(self):
        '''
        Return a list of the 4 locations adjacent to self.

        >>> Location(1, 1).adjacent()
        [Location(row=1, column=2), Location(row=0, column=1), Location(row=1, column=0), Location(row=2, column=1)]
        '''
        return [self.relative(direction) for direction in Direction]
    def diagonals(self):
        '''
        Return a list of the 4 locations diagonaly adjacent to self

        >>> Location(1, 1).diagonals()
        [Location(row=0, column=0), Location(row=0, column=2), Location(row=2, column=0), Location(row=2, column=2)]
        '''
        return [self.path(dir1, dir2)
            for dir1 in (Direction.up, Direction.down)
            for dir2 in (Direction.left, Direction.right)]

    def surrounding(self):
        '''
        Yields each of the 8 locations surrounding self
        '''

        for loc in self.adjacent():
            yield loc

        for loc in self.diagonals():
            yield loc