from gridly.grid.base import GridBase

class CompositeGrid(GridBase):
    ####################################################################
    # Proxy class for access to individual grids
    ####################################################################

    class CompositeGridCellProxy:
        def __init__(self, grid, location):
            self.grid = grid
            self.location = location

        def __getitem__(self, index):
            return self.grid.content[index].unsafe_get(location)

        def __setitem__(self, index, value):
            self.grid.content[index].unsafe_set(location)

        def __len__(self):
            return len(self.grid.content)


    def __init__(self, *grids):
        dimensions = grids[0].dimensions
        for grid in grids[1:]:
            if grid.dimensions != dimensions:
                raise ValueError('All child grids must have the same dimensions',
                    (grids[0], grid))

        GridBase.__init__(self, dimensions[0], dimensions[1], grids)

    def unsafe_get(self, location):
        return CompositeGridCellProxy(self, location)

    def unsafe_set(self, location, value):
        for grid, sub_value in zip(self.grids, value):
            grid.unsafe_set(locations, sub_value)