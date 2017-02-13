from gridly.grid.base import GridBase


class DenseGrid(GridBase):
    '''
    DenseGrid is for grids which have content in most of the cells. It is
    implemented as a list.
    '''
    def __init__(self, num_rows, num_columns, *, fill=None, content=None, func=None):
        GridBase.__init__(self, num_rows, num_columns)
        size = num_rows * num_columns

        if func is not None:
            self.content = list(map(func, self.locations()))
        elif content is not None:
            if len(content) != size:
                raise ValueError("content must have length {}".format(size))
            self.content = list(content)
        else:
            self.content = [fill] * size

    def _index(self, location):
        '''
        Convert a (row, column) tuple to an index. Performs no bounds checking.
        '''
        return (self.num_columns * location[0]) + location[1]

    def unsafe_get(self, location):
        return self.content[self._index(location)]

    def unsafe_set(self, location, value):
        self.content[self._index(location)] = value
