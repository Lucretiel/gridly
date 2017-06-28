import abc

from gridly import Location


# Can't subclass range :(
class Dimension:
    def __init__(self, size):
        self.range = range(0, size, 1)

    def __len__(self):
        return len(self.range)

    # TODO: getitem? It's literally just the identity function with bounds
    # checking

    def __iter__(self):
        return iter(self.range)

    def valid(self, index):
        if not isinstance(index, int):
            raise TypeError(index)

        return index in self.range

    def check(self, index):
        if self.valid(index):
            return index
        else:
            raise IndexError(index)


# All the proxy types assume that validation was already completed on the slice
# they represent
class Proxy:
    def __init__(self, grid, alternate_dim, completer):
        self._unsafe_get = grid.unsafe_get
        self._unsafe_set = grid.unsafe_set
        self._unsafe_complete = completer
        self._alternate_dim = alternate_dim
        self._check = alternate_dim.check

    def _complete_location(self, index):
        return self._unsafe_complete(self._check(index))

    def unsafe_get(self, index):
        return self._unsafe_get(self._unsafe_complete(index))

    def unsafe_get_with_loc(self, index):
        '''
        Return the (location, cell) pair associated with the index
        '''
        loc = self._unsafe_complete(index)
        return loc, self._unsafe_get(loc)

    def unsafe_set(self, index, value):
        return self._unsafe_set(self._unsafe_complete(index), value)

    def __getitem__(self, index):
        return self.unsafe_get(self._check(index))

    def get_with_location(self, index):
        return self.unsafe_get_with_loc(self._check(index))

    def __setitem__(self, index, valus):
        return self.unsafe_set(self._check(index), value)

    def __len__(self):
        return len(self._alternate_dim)

    def __iter__(self):
        get = self.unsafe_get

        for index in self._alternate_dim:
            yield get(index)

    def with_locations(self):
        get = self.unsafe_get_with_loc

        for index in self._alternate_dim:
            yield get(index)


class RowProxy(Proxy):
    def __init__(self, row, grid):
        Proxy.__init__(
            self,
            grid=grid,
            alternate_dim=grid._col_dim,
            completer=lambda column: Location(row, column)
        )


class ColumnProxy(Proxy):
    def __init__(self, column, grid):
        Proxy.__init__(
            self,
            grid=grid,
            alternate_dim=grid._row_dim,
            completer=lambda row: Location(row, column)
        )


class MultiProxy:
    def __init__(self, grid, dimension, ProxyType):
        self._unsafe_proxy = lambda index: ProxyType(index, grid)
        self._dimension = dimension
        self._check = dimension.check

    def __len__(self):
        return len(self._index_range)

    def __getitem__(self, index):
        return self._unsafe_proxy(self._check(index))

    def __iter__(self):
        make_proxy = self._unsafe_proxy

        for index in self._index_range:
            yield make_proxy(index)


class RowsProxy(MultiProxy):
    def __init__(self, grid):
        MultiProxy.__init__(
            self,
            grid=grid,
            dimension=grid._row_dim,
            ProxyType=RowProxy
        )


class ColumnsProxy(MultiProxy):
    def __init__(self, grid):
        MultiProxy.__init__(
            self,
            grid=grid,
            dimension=grid._col_dim,
            ProxyType=ColumnProxy
        )


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

    def __init__(self, num_rows, num_columns):
        self._row_dim = Dimension(num_rows)
        self._col_dim = Dimension(num_columns)

        self.dimensions = self.num_rows, self.num_columns = num_rows, num_columns

        self.valid_row = self._row_dim.valid
        self.valid_column = self._col_dim.valid

        self.check_row = self._row_dim.check
        self.check_column = self._col_dim.check

    ####################################################################
    # Bounds Checkers
    ####################################################################

    def valid_location(self, location):
        '''
        Return true if a location is in the bounds of this grid. Raise a TypeError
        if location is not a valid location type, which is loosely defined as a
        subscriptable container of two ints.
        '''
        if len(location) != 2:
            raise TypeError(location)

        try:
            return self.valid_row(location[0]) and self.valid_column(location[1])
        except TypeError as e:
            raise TypeError(location) from e

    def check_location(self, location):
        '''
        Return the location if it is valid. Raise IndexError otherwise. May
        also raise a TypeError if location is an invalid type.
        '''
        if len(location) != 2:
            raise TypeError(location)

        try:
            self.check_row(location[0])
            self.check_column(location[1])
            return location
        except IndexError as e:
            raise IndexError(location) from e
        except TypeError as e:
            raise TypeError(location) from e

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
        Return an iterable RowProxy to the given row.
        '''
        return RowProxy(row, self)

    def unsafe_column(self, column):
        '''
        Return an iterable ColumnProxy to the given column.
        '''
        return ColumnProxy(column, self)

    def unsafe_cells(self, locations):
        '''
        Given an iterable of locations, yield all (location, cell) pairs.
        Performs no bounds checking on the location.
        '''
        unsafe_get = self.unsafe_get
        for location in locations:
            yield location, unsafe_get(location)

    def row(self, row):
        '''
        Return an iterable proxy for all the rows in the grid
        '''
        return RowsProxy(self)

    def column(self, column):
        '''
        Return an iterable proxy for all the rows in the grid
        '''
        return self.unsafe_column(self.check_column(column))

    def rows(self):
        '''
        Iterate over each row. Each row is an iterable, containing each cell in
        the row
        '''
        return map(self.unsafe_row, self._row_range)

    def columns(self):
        '''
        Iterate over each columns. Each column is an iterable, containing each
        cell in the column
        '''
        return map(self.unsafe_column, self._col_range)

    def locations(self):
        '''
        Iterate over each location on the grid in row-major order
        '''
        col_range = self._col_range
        for row in self._row_range:
            for column in col_range:
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
