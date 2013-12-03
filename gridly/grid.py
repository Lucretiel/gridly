import copy

class GridMixin:
    def __init__(self, num_rows, num_columns, content):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.content = content

    def valid(self, location):
        return (0 <= location[0] < self.num_rows and
            0 <= location[1] < self.num_columns)

    def __getitem__(self, location):
        if self.valid(location):
            return self.unsafe_get(location)
        else:
            raise IndexError(location)

    def __setitem__(self, location, value):
        if self.valid(location):
            return self.unsafe_set(location, value)
        else:
            raise IndexError(location)

    def row(self, row):
        for column in range(self.num_columns):
            yield self.unsafe_get((row, column))

    def column(self, column):
        for row in range(self.num_rows):
            yield self.unsafe_get((row, column))

    def rows(self):
        for row in range(self.num_rows):
            yield self.row(row)

    def columns(self):
        for column in range(self.num_columns):
            yield self.column(column)

    def copy(self):
        return type(self)(self.num_rows, self.num_columns, content=copy.copy(self.content))

class DenseGrid(GridMixin):
    def __init__(num_rows, num_columns, fill=None, content=None):
        if content is None:
            content = [fill] * num_rows * num_columns
        GridMixin.__init__(self, num_rows, num_columns, content)

    def index(self, location):
        return (self.num_columns * location[0]) + location[1]

    def unsafe_get(self, location):
        return self.content[self.index(location)]

    def unsafe_set(self, location, value):
        self.content[self.index(location)] = value


class SparseGrid(GridMixin):
    def __init__(num_rows, num_columns, fill=None, content=None):
        if content is None:
            content = {}
        GridMixin.__init__(self, num_rows, num_columns, content)
        self.fill = fill

    def unsafe_get(self, location):
        return self.content.get(tuple(location), self.fill)

    def unsafe_set(self, location, value):
        location = tuple(location)
        if value is self.fill:
            self.content.pop(location, None)
        else:
            self.content[location] = value
