def check_range(valye, max):
    '''
    return true if value between 0 and max (max is exclusive)
    '''
    return (0 <= value < max)

class GridMixin:
    '''
    Mixin to provide common functionality to Grids. Grid concrete classes should
    implement `unsafe_get`, `unsafe_set`, and `__init__(num_rows, num_columns,
    content=content)`
    '''
    def __init__(self, num_rows, num_columns, content):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.content = content

    def valid_row(self, row):
        return check_range(row, self.num_rows)

    def valid_column(self, column):
        return check_range(column, self.num_columns)

    def valid(self, location):
        '''
        Return true if a location is valid
        '''
        return self.valid_row(location[0]) and self.valid_column(location[1])

    def check_location(self, location):
        '''
        Return location if a location is valid. Raise IndexError otherwise.
        '''
        #TODO: Check back here as a candidate for "inner loop" optimiztion
        if self.valid(location):
            return location
        else:
            raise IndexError(location)

    def __getitem__(self, location):
        return self.unsafe_get(self.check_location(location))

    def __setitem__(self, location, value):
        return self.unsafe_set(self.check_location(location), value)

    def row(self, row):
        '''
        Iterate over all the cells in a row
        '''
        for column in range(self.num_columns):
            yield self.unsafe_get((row, column))

    def column(self, column):
        '''
        Iterate over all the cells in a column
        '''
        for row in range(self.num_rows):
            yield self.unsafe_get((row, column))

    def rows(self):
        '''
        Iterate over each row. Each row is an iterable, containing each cell in
        the row
        '''
        for row in range(self.num_rows):
            yield self.row(row)

    def columns(self):
        '''
        Iterate over each columns. Each column is an iterable, containing each
        cell in the column
        '''
        for column in range(self.num_columns):
            yield self.column(column)
