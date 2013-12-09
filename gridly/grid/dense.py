from .base import GridMixin

class DenseGrid(GridMixin):
    '''
    DenseGrid is for grids which have content in most of the cells. It is
    implemented as a list.
    '''
    def __init__(self, num_rows, num_columns, fill=None, content=None):
        if content is None:
            content = [fill] * num_rows * num_columns
        GridMixin.__init__(self, num_rows, num_columns, content)

    def index(self, location):
        '''
        Convert a (row, column) tuple to an index. Performs no bounds checking.
        '''
        return (self.num_columns * location[0]) + location[1]

    def unsafe_get(self, location):
        return self.content[self.index(location)]

    def unsafe_set(self, location, value):
        self.content[self.index(location)] = value

    def row(self, row):
        '''
        Specialized implementation of the row iterator
        '''
        if not self.valid_row(row):
            raise IndexError(row)
        start = self.index((row, 0))
        return self.content[start:(start+self.num_columns)]
