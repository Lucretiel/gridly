import abc
from gridly import Location


class GridBase(metaclass=abc.ABCMeta):
    '''
    Base class to provide common functionality to Grids. Grid concrete
    classes should implement `unsafe_get` and `unsafe_set`.

    All `unsafe_*` methods do not perform any bounds checking or type checking
    on their arguments. Users should prefer to use the safe versions, which
    do perform the checking, and are optimized to only do that checking as few
    times as possible. For instance, the grid.row(row_index) method (which
    iterates over all cells in a row) only bounds-checks the row once.
    '''

    def __init__(self, num_rows, num_columns, content):
        self._row_range = range(num_rows)
        self._col_range = range(num_columns)
        self.content = content

    @property
    def num_rows(self):
        return len(self._row_range)

    @property
    def num_columns(self):
        return len(self._col_range)

    @property
    def dimensions(self):
        return self.num_rows, self.num_columns

    ####################################################################
    # Bounds Checkers
    ####################################################################

    # TODO: these are inner-loop functions. Determine if they should be optimized.
    def valid_row(self, row):
        '''
        return true if the row is in the bounds of this grid. Raise a TypeError
        if row is not an int.
        '''
        if not isinstance(row, int):
            raise TypeError(row)

        return row in self._row_range

    def valid_column(self, column):
        '''
        return true if the column is in the bounds of this grid. Raise a TypeError
        if column is not an int.
        '''
        if not isinstance(column, int):
            raise TypeError(column)

        return column in self._col_range

    def valid(self, location):
        '''
        Return true if a location is in the bounds of this grid. Raise a TypeError
        if location is not a valid location type, which is loosely defined as a
        container of two ints.
        '''
        if len(location) != 2:
            raise TypeError(location)

        try:
            return self.valid_row(location[0]) and self.valid_column(location[1])
        except TypeError as e:
            raise TypeError(location) from e

    def check_row(self, row):
        '''
        Return the row if it is in the bounds. Raise IndexError otherwise. May
        also raise a TypeError if row is an invalid type.
        '''
        if self.valid_row(row):
            return row
        else:
            raise IndexError(row)

    def check_column(self, column):
        '''
        Return the row if it is in the bounds. Raise IndexError otherwise. May
        also raise a TypeError if location is an invalid type.
        '''
        if self.valid_column(column):
            return column
        else:
            raise IndexError(column)

    def check_location(self, location):
        '''
        Return the location if it is valid. Raise IndexError otherwise. May
        also raise a TypeError if location is an invalid type.
        '''
        if self.valid(location):
            return location
        else:
            raise IndexError(location)

    ####################################################################
    # Basic element access
    ####################################################################
    @abc.abstractmethod
    def unsafe_get(self, location):
        raise NotImplementedError

    @abc.abstractmethod
    def unsafe_set(self, location, value):
        raise NotImplementedError

    def __getitem__(self, location):
        '''
        Perform a checked lookup. Raises IndexError if location is out of range.
        '''
        return self.unsafe_get(self.check_location(location))

    def __setitem__(self, location, value):
        '''
        Perform a checked set. Raises IndexError if location is out of range.
        '''
        self.unsafe_set(self.check_location(location), value)

    get = __getitem__
    set = __setitem__

    ####################################################################
    # Iterators
    ####################################################################
    # Note: the iterators that iterate over individual rows or columns do not
    # provide the location objects. The assumption is that the user can
    # enumerate() them if they need those indexes. Iterators that yield
    # other cell sets include the location. For instance:

    # for row_index, row in enumerate(grid.rows()):
    #     for col_index, cell in enumerate(row):
    #         loc = Location(row_index, column_index)
    #
    # Equivelent to:
    #
    # for loc in grid.cells():
    #    row_index, col_index = loc

    def unsafe_row(self, row):
        '''
        Iterate over all the cells in a row. Performs no range checking.
        '''
        unsafe_get = self.unsafe_get
        for column in self._col_range:
            yield unsafe_get((row, column))

    def unsafe_column(self, column):
        '''
        Iterate over all the cells in a column. Performs no range checking.
        '''
        unsafe_get = self.unsafe_get
        for row in self._row_range:
            yield unsafe_get((row, column))

    def unsafe_cells(self, locations):
        '''
        Given an iterable of locations, iterate over (cell, location) pairs.
        Performs no bounds checking on the location.
        '''
        unsafe_get = self.unsafe_get
        for location in locations:
            yield location, unsafe_get(location)

    def row(self, row):
        '''
        Iterate over all the cells in a row. Raises IndexError if row is out of range
        '''
        return self.unsafe_row(self.check_row(row))

    def column(self, column):
        '''
        Iterate over all the cells in a column
        '''
        return self.unsafe_column(self.check_column(column))

    def rows(self):
        '''
        Iterate over each row. Each row is an iterable, containing each cell in
        the row
        '''
        unsafe_row = self.unsafe_row
        for row in self._row_range:
            yield unsafe_row(row)

    def columns(self):
        '''
        Iterate over each columns. Each column is an iterable, containing each
        cell in the column
        '''
        unsafe_column = self.unsafe_column
        for column in self._col_range:
            yield unsafe_column(column)

    def locations(self):
        '''
        Iterate over each location on the grid in row-major order
        '''
        for row in self._row_range:
            for column in self._col_range:
                yield Location(row, column)

    def cells(self, locations=None):
        '''
        Iterate over (location, cell) pairs for all locations in row-major
        order. If locations is given, it should be an iterable of locations
        that will be used instead of all locations. An IndexError will be
        raised on the first invalid location
        '''
        if locations is None:
            return self.unsafe_cells(self.locations())
        else:
            return self.unsafe_cells(map(self.check_location, locations))

    def in_bounds(self, locations):
        '''
        Given an iterable of locations, yield all the locations that are within
        the bounds of this grid.
        '''
        return filter(self.valid, locations)

    def cells_in_bounds(self, locations):
        '''
        Given an iterable of locations, yield (location, cell) pairs for all
        the locations that are within the bounds of the grid
        '''
        return self.unsafe_cells(self.in_bounds(locations))
